import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='{PROJECT_NAME}',                            # should match the package folder
    packages=['{PROJECT_NAME}'],                      # should match the package folder
    version='0.0.0',                                # UPDATE
    license='MIT',                                  # should match your chosen license
    description='',                                 # UPDATE
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Mike Huls',
    author_email='m.huls@datanext.nl',
    url='https://github.com/profile/project',       # UPDATE 
    project_urls = {                                # Optional
        # "Bug Tracker": "https://github.com/profile/project/issues"
    },
    install_requires=[],                            # ADD -> list all packages that your package uses
    keywords=[],                                    # ADD
    classifiers=[                                   # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)