from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

test_reqs = []

doc_reqs = [
    'Sphinx>=1.5.2'
]

extra_reqs = {
    'doc': doc_reqs,
    'test': test_reqs
}

install_requires = [
    'Django>=3.0.0',
    'psycopg2',
]

setup(
    name='musika',
    version='0.1',
    description='My Collection Library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@osharabi",
    author_email="osharabi@gmail.com",
    url='http://noneyet/',
    install_requires=install_requires,
    tests_require=test_reqs,
    extras_require=extra_reqs,
    license='LICENSE.md',
    packages=['musika'],
    scripts=["manage.py", "scripts/ingest_db.py"],
)