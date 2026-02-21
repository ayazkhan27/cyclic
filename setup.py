from setuptools import setup, find_packages, Extension

ckhan_ext = Extension(
    'khan_cipher.ckhan',
    sources=['src/khan_cipher/c_ext/khan_core.cpp'],
    extra_compile_args=['-O3', '-std=c++17', '-march=native'],
    libraries=['crypto']
)

setup(
    name='khan_cipher',
    version='1.0.0',
    description='A high-performance primitive root stream cipher',
    author='Ayaz Khan',
    author_email='ayaz@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    ext_modules=[ckhan_ext],
    python_requires='>=3.8',
    install_requires=[
        'cryptography>=41.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: C++'
    ]
)
