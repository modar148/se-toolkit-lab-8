import re

with open('/root/se-toolkit-lab-8/docker-compose.yml') as f:
    lines = f.readlines()

result = []
skip_until_otel = False
for line in lines:
    if '# Task 2A' in line and 'uncomment' in line:
        skip_until_otel = True
        result.append('  nanobot:\n')
        continue
    if skip_until_otel:
        if '#     - otel-collector' in line:
            result.append('      - otel-collector\n')
            skip_until_otel = False
        elif line.startswith('  #'):
            result.append(line[2:])
        continue
    result.append(line)

with open('/root/se-toolkit-lab-8/docker-compose.yml', 'w') as f:
    f.writelines(result)
print('Done')
