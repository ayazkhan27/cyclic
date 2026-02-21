#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <vector>
#include <cstdint>

struct KeystreamState { 
    std::vector<uint8_t> cyclic_sequence; 
    size_t position; 
};

static PyObject* c_bulk_xor(PyObject* self, PyObject* args) {
    const uint8_t* data;
    Py_ssize_t data_len;
    const uint8_t* keystream;
    Py_ssize_t key_len;

    if (!PyArg_ParseTuple(args, "y#y#", &data, &data_len, &keystream, &key_len)) {
        return NULL;
    }

    if (data_len != key_len) {
        PyErr_SetString(PyExc_ValueError, "Length mismatch between data and keystream");
        return NULL;
    }

    uint8_t* output = new uint8_t[data_len];
    
    for (Py_ssize_t i = 0; i < data_len; ++i) {
        output[i] = data[i] ^ keystream[i];
    }

    PyObject* result = PyBytes_FromStringAndSize((char*)output, data_len);
    delete[] output;
    
    return result;
}

static PyMethodDef ckhan_methods[] = {
    {"bulk_xor", c_bulk_xor, METH_VARARGS, "Fast bulk XOR."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ckhan_module = {
    PyModuleDef_HEAD_INIT,
    "ckhan",
    "C++ Backend for KHAN Cipher",
    -1,
    ckhan_methods
};

PyMODINIT_FUNC PyInit_ckhan(void) {
    return PyModule_Create(&ckhan_module);
}
