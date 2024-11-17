# Instructions

create virtual environment

```bash
python3 -m venv venv
```

Activate virtual env

```bash
source .virt/bin/activate.fish
```

Install packages

```bash
pip install -r requirements.txt
```

Run app

```bash
python3 -m src.app
```

init db

```bash
flask db init
```

set flask app env variable

```bash
export FLASK_APP=src.app
```

run migration

```bash
flask db migrate -m "message"
```

update database

```bash
flask db upgrade
```
