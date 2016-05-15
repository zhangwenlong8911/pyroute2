#include <sys/types.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include "Python.h"


static PyObject *
sock_send_from(PyObject *self, PyObject *args)
{
    int fd;
    long n = -1;
    struct sockaddr_nl dest;
    Py_buffer buf;

    if (!PyArg_ParseTuple(args, "iw*:send_from", &fd, &buf))
        return NULL;

    assert(buf.buf != 0 && buf.len > 0);
    dest.nl_family = AF_NETLINK;
    dest.nl_pid = 0;
    dest.nl_groups = 0;

    Py_BEGIN_ALLOW_THREADS
    n = sendto(fd, buf.buf, buf.len, 0, (struct sockaddr*)&dest, sizeof(struct sockaddr_nl));
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&buf);
    return PyInt_FromLong((long)n);
}
PyDoc_STRVAR(sock_send_from_doc,
"sock_send_from(fd, buf, [len, [flags, [addr]]]) -> bytes_sent\n\
\n\
Warning: it is an unsafe by design function. Please, do not use\n\
it unless you understand its C code and why it is written.");


PyDoc_STRVAR(send_doc, "unsafe send\n");


static PyMethodDef send_methods[] = {
    {"send_from", sock_send_from, METH_VARARGS, sock_send_from_doc},
    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
initsend(void)
{
    PyObject *m;
    m = Py_InitModule3("send", send_methods, send_doc);
    if (m == NULL)
        return;
}
