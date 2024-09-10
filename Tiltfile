# Use docker-compose for local development
docker_compose('docker-compose.yml')

# Define a custom build for the gmail_to_weaviate service
docker_build('gmail_to_weaviate', '.',
    live_update=[
        # Sync local files to the container
        sync('.', '/app'),
        # Restart the Flask server when Python files change
        run('pip install -r requirements.txt', trigger='requirements.txt'),
        restart_container()
    ])

# Forward ports
forward_port('gmail_to_weaviate', 5000)
forward_port('weaviate', 8080)

# Watch for changes in Python files and requirements
watch_file('*.py')
watch_file('utils/*.py')
watch_file('templates/*.html')
watch_file('static/**')
watch_file('requirements.txt')

# Add a resource to run tests
local_resource(
    'run tests',
    'pytest tests/',
    deps=['tests'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL
)

# Add a resource for linting
local_resource(
    'lint',
    'flake8 .',
    deps=['.'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL
)
