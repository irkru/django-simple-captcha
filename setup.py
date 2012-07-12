from setuptools import setup, find_packages
setup(
    name='django-simple-redis-captcha',
    version='0.3.5',
    description='A very simple, yet powerful, Django captcha application empowered with Redis',
    author='Marco Bonetti',
    author_email='mbonetti@gmail.com',
    url='https://github.com/irkru/django-simple-captcha',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    requires=['PIL (>=1.1.6)', 'redis>=2.0.0']
)
