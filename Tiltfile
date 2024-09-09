docker_compose('docker-compose.yml')

# Build the gmail_to_weaviate service
docker_build('gmail_to_weaviate', '.')

# Forward ports
forward_port('weaviate', 8080)

# Watch for changes in Python files and requirements
watch_file('*.py')
watch_file('requirements.txt')
