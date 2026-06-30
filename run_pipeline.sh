#!/bin/bash
# Navigate to your project directory
cd ~/permitflow-nj

# Run the state data harvest
/usr/bin/python3 sync_licenses.py

# Run the Deal Scout AI analyzer
/usr/bin/python3 scout_analysis.py

echo "Pipeline auto-run finished at $(date)" >> automation.log