# Bot API Documentation

## Overview

The Modern Host Watch Bot provides a comprehensive set of commands for monitoring hosts and services through Telegram. This document describes all available commands, their parameters, and usage examples.

## Command Categories

### 1. Basic Commands
Essential commands for bot interaction and help.

### 2. Host Management
Commands for adding, removing, and managing monitored hosts.

### 3. Manual Checks
Commands for performing manual connectivity tests.

### 4. Configuration
Commands for customizing monitoring settings.

### 5. Reports
Commands for viewing status and failure reports.

### 6. Admin Commands
Commands restricted to administrators for system management.

## Basic Commands

### `/start`
**Description**: Initialize the bot and get welcome message.

**Usage**: `/start`

**Response**: Welcome message with bot information and quick start guide.

**Example**:
```
/start
```

### `/help`
**Description**: Show comprehensive help and available commands.

**Usage**: `/help`

**Response**: Detailed help message with all available commands.

**Example**:
```
/help
```

## Host Management Commands

### `/pingadd`
**Description**: Add a host to monitoring.

**Usage**: `/pingadd <host> <interval> [port]`

**Parameters**:
- `host` (required): Host IP address or domain name
- `interval` (required): Check interval in seconds (120-2400)
- `port` (optional): TCP port to check (default: 80)

**Response**: Confirmation message with host details.

**Examples**:
```
/pingadd google.com 300
/pingadd 192.168.1.1 600 443
/pingadd api.example.com 120 8080
```

**Error Cases**:
- Invalid host address
- Interval outside allowed range
- Host already being monitored
- User limit exceeded

### `/pingdelete`
**Description**: Remove a host from monitoring.

**Usage**: `/pingdelete <host>`

**Parameters**:
- `host` (required): Host IP address or domain name

**Response**: Confirmation message.

**Examples**:
```
/pingdelete google.com
/pingdelete 192.168.1.1
```

**Error Cases**:
- Host not being monitored
- Invalid host address

### `/pinglist`
**Description**: List monitored hosts.

**Usage**: `/pinglist [all]`

**Parameters**:
- `all` (optional): Show all hosts (admin only)

**Response**: Formatted table with host status.

**Examples**:
```
/pinglist
/pinglist all
```

**Response Format**:
```
Your Monitored Hosts:
🟢✅ `80  ` `300s   ` `14:30` `Now` [google.com](https://google.com)
🔴❌ `443 ` `600s   ` `14:25` `Now` [api.example.com](https://api.example.com)
```

## Manual Check Commands

### `/pinghost`
**Description**: Perform manual ping check.

**Usage**: `/pinghost <host>`

**Parameters**:
- `host` (required): Host IP address or domain name

**Response**: Ping result with response time.

**Examples**:
```
/pinghost google.com
/pinghost 192.168.1.1
```

**Response Format**:
```
🟢 Manual Ping Result

Host: `google.com`
Status: Online (45ms)
Time: 2024-01-15 14:30:25
```

### `/pinghostport`
**Description**: Check if a TCP port is open.

**Usage**: `/pinghostport <host> <port>`

**Parameters**:
- `host` (required): Host IP address or domain name
- `port` (required): Port number to check

**Response**: Port check result.

**Examples**:
```
/pinghostport google.com 443
/pinghostport 192.168.1.1 22
```

**Response Format**:
```
✅ Port Check Result

Host: `google.com`
Port: `443`
Status: Open
Time: 2024-01-15 14:30:25
```

## Configuration Commands

### `/pinginterval`
**Description**: Change monitoring interval for a host.

**Usage**: `/pinginterval <host> <seconds>`

**Parameters**:
- `host` (required): Host IP address or domain name
- `seconds` (required): New interval in seconds (120-2400)

**Response**: Confirmation with old and new intervals.

**Examples**:
```
/pinginterval google.com 600
/pinginterval api.example.com 300
```

### `/changepingport`
**Description**: Change the monitored port for a host.

**Usage**: `/changepingport <host> <port>`

**Parameters**:
- `host` (required): Host IP address or domain name
- `port` (required): New port number

**Response**: Confirmation with old and new ports.

**Examples**:
```
/changepingport google.com 443
/changepingport api.example.com 8080
```

### `/storecredentials`
**Description**: Store SSH credentials for a host.

**Usage**: 
- Store: `/storecredentials <host> <username> <password> [port]`
- Show: `/storecredentials <host>`

**Parameters**:
- `host` (required): Host IP address or domain name
- `username` (required for store): SSH username
- `password` (required for store): SSH password
- `port` (optional): SSH port (default: 22)

**Response**: Confirmation or display of stored credentials.

**Examples**:
```
/storecredentials myserver admin mypassword
/storecredentials myserver admin mypassword 2222
/storecredentials myserver
```

### `/pinglog`
**Description**: Toggle success notification logs.

**Usage**: `/pinglog`

**Response**: Status of success logs (enabled/disabled).

**Example**:
```
/pinglog
```

## Report Commands

### `/listfailures`
**Description**: Show recent host failures.

**Usage**: `/listfailures`

**Response**: List of hosts with failure timestamps.

**Example**:
```
/listfailures
```

**Response Format**:
```
Host Failures:
`2024-01-15 14:25` [api.example.com](https://api.example.com) - Offline
`2024-01-15 13:45` [myserver.com](https://myserver.com) - Port Closed
```

## Admin Commands

### `/exec`
**Description**: Execute local command (admin only).

**Usage**: `/exec <command>`

**Parameters**:
- `command` (required): Command to execute

**Response**: Command output or error message.

**Examples**:
```
/exec uptime
/exec df -h
/exec ps aux
```

**Security**: Restricted to admin users only.

### `/ssh`
**Description**: Execute SSH command on remote host (admin only).

**Usage**: `/ssh <host> <command>`

**Parameters**:
- `host` (required): Host IP address or domain name
- `command` (required): SSH command to execute

**Response**: Command output or error message.

**Examples**:
```
/ssh myserver uptime
/ssh myserver df -h
/ssh myserver systemctl status nginx
```

**Prerequisites**: SSH credentials must be stored with `/storecredentials`.

## Error Responses

All commands return standardized error messages:

### Format
```
❌ Error: <error_description>
```

### Common Error Types

1. **Validation Errors**:
   ```
   ❌ Error: Interval must be between 120 and 2400 seconds
   ```

2. **Permission Errors**:
   ```
   ❌ Error: This command is restricted to administrators
   ```

3. **Not Found Errors**:
   ```
   ❌ Error: Host 'example.com' is not being monitored
   ```

4. **Configuration Errors**:
   ```
   ❌ Error: No SSH credentials found for host 'example.com'
   ```

5. **System Errors**:
   ```
   ❌ Error: An unexpected error occurred
   ```

## Response Formatting

### Markdown Support
All responses use Telegram's MarkdownV2 format for rich text:

- **Bold text**: `*text*`
- **Code blocks**: `` `code` ``
- **Links**: `[text](url)`
- **Escape characters**: `\` for special characters

### Status Icons
- 🟢 Online/Open
- 🔴 Offline/Closed
- ✅ Success
- ❌ Failure
- ⚠️ Warning
- ℹ️ Information

## Rate Limiting

- Commands are processed sequentially per user
- Network operations have configurable timeouts
- Database operations are optimized for performance

## Security Considerations

1. **Input Validation**: All parameters are validated
2. **Access Control**: Admin commands require proper permissions
3. **Credential Security**: SSH passwords are encrypted
4. **Error Handling**: No sensitive information in error messages

## Best Practices

1. **Use descriptive host names**: `web-server-prod` instead of `192.168.1.1`
2. **Set appropriate intervals**: 300s for critical services, 600s for others
3. **Monitor relevant ports**: 80/443 for web services, 22 for SSH
4. **Store SSH credentials**: Enable remote command execution
5. **Regular monitoring**: Check `/pinglist` periodically

## Troubleshooting

### Common Issues

1. **Host not responding**:
   - Check if host is reachable from bot server
   - Verify firewall settings
   - Test with `/pinghost` command

2. **Port check failing**:
   - Verify service is running on target port
   - Check firewall rules
   - Test with `/pinghostport` command

3. **SSH connection failing**:
   - Verify SSH credentials with `/storecredentials`
   - Check SSH service is running
   - Verify network connectivity

4. **Bot not responding**:
   - Check bot token in configuration
   - Verify bot is running
   - Check logs for errors 