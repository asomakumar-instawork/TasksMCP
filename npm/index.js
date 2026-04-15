#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

const MCP_URL = 'https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp';

const token = process.argv[2] || process.env.TASKS_MCP_TOKEN;

if (!token) {
  console.error('Error: token required.');
  console.error('Usage:   npx tasksmcp YOUR_TOKEN_HERE');
  console.error('Or set:  TASKS_MCP_TOKEN=YOUR_TOKEN_HERE');
  process.exit(1);
}

const mcpRemote = path.join(__dirname, 'node_modules', '.bin', 'mcp-remote');

const child = spawn(mcpRemote, [
  MCP_URL,
  '--transport', 'http-only',
  '--header', `Authorization:Bearer ${token}`
], { stdio: 'inherit' });

child.on('exit', (code) => process.exit(code || 0));
