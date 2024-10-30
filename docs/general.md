
Get script name and line number that throws last error

```
logger.error(f"An error occurred in {__file__} at line {e.__traceback__.tb_lineno}: {e}")
```
