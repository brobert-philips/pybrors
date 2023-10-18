# Introduction

*pybrors* is a Python/Rust package gathering several tools developed for Clinical Science purposes. As a Python/Rust package, users should control if the rust library (rust_lib) is properly installed.

Examples of *pybrors* use are accessible in the "ext" directory with Jupyter notebooks. It should be noted that package test was limited, and there might be bugs or errors. Issues or bug report are more than welcomed to improve the stability of this package.

# Installation

Package should be downloaded from its [*pybrors* github page](https://github.com/brobert-philips/pybrors.git).

It is recommended to create python virtual environment at the root of the package directory. Within this virtual environment, it is important to install the *maturin* package which is used to generate the Rust library which is optimizing data processing.

To generate Rust library, you should type in a terminal for the debug version of the Rust library.

```bash
.venv/bin/maturin develop
```

You should use `release` instead of `debug` for the released version of the Rust library.

# API documentation

You can access [API documentation](docs/index.html).
