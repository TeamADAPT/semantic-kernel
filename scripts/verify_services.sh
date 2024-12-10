#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Verifying services after scale-up to c3-highmem-176...${NC}"

# Check ChromaDB service
echo -e "\n${YELLOW}Checking ChromaDB service...${NC}"
if systemctl is-active --quiet chromadb; then
    echo -e "${GREEN}ChromaDB service is running${NC}"
    # Verify port is listening
    if netstat -tuln | grep -q ":8000 "; then
        echo -e "${GREEN}ChromaDB port 8000 is listening${NC}"
    else
        echo -e "${RED}ERROR: ChromaDB port 8000 is not listening${NC}"
        exit 1
    fi
    # Check memory allocation
    CHROMA_MEM=$(ps -o rss= -p $(systemctl show -p MainPID chromadb | cut -d= -f2))
    echo "ChromaDB memory usage: $((CHROMA_MEM/1024)) MB"
else
    echo -e "${RED}ERROR: ChromaDB service is not running${NC}"
    systemctl status chromadb
    exit 1
fi

# Check Semantic Kernel service
echo -e "\n${YELLOW}Checking Semantic Kernel service...${NC}"
if systemctl is-active --quiet semantic-kernel; then
    echo -e "${GREEN}Semantic Kernel service is running${NC}"
    # Verify port is listening
    if netstat -tuln | grep -q ":3000 "; then
        echo -e "${GREEN}Semantic Kernel API port 3000 is listening${NC}"
    else
        echo -e "${RED}ERROR: Semantic Kernel API port 3000 is not listening${NC}"
        exit 1
    fi
    # Check memory allocation
    SK_MEM=$(ps -o rss= -p $(systemctl show -p MainPID semantic-kernel | cut -d= -f2))
    echo "Semantic Kernel memory usage: $((SK_MEM/1024)) MB"
else
    echo -e "${RED}ERROR: Semantic Kernel service is not running${NC}"
    systemctl status semantic-kernel
    exit 1
fi

# Verify data persistence
echo -e "\n${YELLOW}Checking data persistence...${NC}"
if [ -d "/data/chroma" ]; then
    echo -e "${GREEN}ChromaDB data directory exists${NC}"
    # Check permissions
    if [ "$(stat -c '%U:%G' /data/chroma)" = "nova:nova" ]; then
        echo -e "${GREEN}ChromaDB data directory has correct permissions${NC}"
    else
        echo -e "${RED}ERROR: ChromaDB data directory has incorrect permissions${NC}"
        ls -l /data/chroma
        exit 1
    fi
else
    echo -e "${RED}ERROR: ChromaDB data directory is missing${NC}"
    exit 1
fi

# Verify memory limits
echo -e "\n${YELLOW}Checking memory limits...${NC}"
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
echo "Total system memory: ${TOTAL_MEM}GB"
if [ $TOTAL_MEM -ge 1400 ]; then
    echo -e "${GREEN}System has expected memory for c3-highmem-176${NC}"
else
    echo -e "${RED}WARNING: System memory is less than expected for c3-highmem-176${NC}"
fi

# Verify API health
echo -e "\n${YELLOW}Checking API health...${NC}"
if curl -s -f http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}API health check passed${NC}"
else
    echo -e "${RED}ERROR: API health check failed${NC}"
    exit 1
fi

# Verify ChromaDB connectivity
echo -e "\n${YELLOW}Checking ChromaDB connectivity...${NC}"
if curl -s -f http://localhost:8000/api/v1/heartbeat > /dev/null; then
    echo -e "${GREEN}ChromaDB connectivity check passed${NC}"
else
    echo -e "${RED}ERROR: ChromaDB connectivity check failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}All services verified successfully after scale-up!${NC}"
exit 0
