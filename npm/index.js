#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const MCP_URL = 'https://errands.instawork.ai/mcp';

const token = process.argv[2] || process.env.TASKS_MCP_TOKEN;

if (!token) {
  console.error('Error: token required.');
  console.error('Usage:   npx instawork-mcp YOUR_TOKEN_HERE');
  console.error('Or set:  TASKS_MCP_TOKEN=YOUR_TOKEN_HERE');
  process.exit(1);
}

const mcpArgs = [
  MCP_URL,
  '--transport', 'http-only',
  '--header', `Authorization:Bearer ${token}`
];

const localMcpRemote = path.join(__dirname, 'node_modules', '.bin', 'mcp-remote');

let cmd, args;
if (fs.existsSync(localMcpRemote)) {
  cmd = localMcpRemote;
  args = mcpArgs;
} else {
  cmd = path.join(path.dirname(process.execPath), 'npx');
  args = ['-y', 'mcp-remote', ...mcpArgs];
}

const child = spawn(cmd, args, { stdio: 'inherit' });

child.on('exit', (code) => process.exit(code || 0));
