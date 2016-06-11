Environmental variables
==========================

jps uses below environmental variables. These are optional.
You don't need to set these variables (default will be used.)

- `JPS_MASTER_HOST`: set default master host. (default: "localhost")
- `JPS_SUFFIX`: Add this to all topic names. This is for multi robot system. (default: "")
- `JPS_MASTER_PUB_PORT`: port number for publishers (default: 54320)
- `JPS_MASTER_SUB_PORT`: port number for subscribers (default: 54321)
- `JPS_SERIALIZE`: default serialzier. Only 'json' is supported. (default: None)
- `JPS_REMAP`: remap topic names. If you set 'export JPS_REMAP="hoge=foo"', topic 'hoge' will be changed to 'foo'
