#!/bin/sh
# Run Django unit tests inside Docker (so face_recognition and all deps are available).
# Usage: ./run_tests.sh   or: docker-compose run --rm web python facial_recognition_system/manage.py test authentication -v 2
set -e
docker-compose run --rm web python facial_recognition_system/manage.py test authentication -v 2
