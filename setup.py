import setuptools

with open('readme.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='md.message.rabbitmq.pika',
    version='0.3.0',
    description='Provides rabbitmq client implementation of md.message contract on top of pika',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='License :: OSI Approved :: MIT License',
    package_dir={'': 'lib'},
    py_modules=['md.message.rabbitmq.pika'],
    install_requires=['md.message==0.2.*', 'pika>=1.2'],
    dependency_links=[
        'https://source.md.land/python/md-message/'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
