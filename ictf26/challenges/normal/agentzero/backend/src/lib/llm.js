const OpenAI = require('openai');
const { randomBytes } = require('crypto');

const llmClient = new OpenAI({
  baseURL: process.env.LLM_BASE_URL,
  apiKey: process.env.LLM_API_KEY,
});

const MODEL = process.env.LLM_MODEL;

const FLAG_VAULT_ID = randomBytes(4).toString('hex');

const VAULT_LIST = [
  { id: randomBytes(4).toString('hex'), name: 'user-preferences', access: 'public' },
  { id: randomBytes(4).toString('hex'), name: 'audit-logs', access: 'internal' },
  { id: FLAG_VAULT_ID, name: 'classified', access: 'restricted' },
  { id: randomBytes(4).toString('hex'), name: 'system-config', access: 'public' },
].sort(() => Math.random() - 0.5);

const LIST_VAULTS_TOOL = {
  type: 'function',
  function: {
    name: 'listVaults',
    description: 'List all available vaults and their access levels.',
    parameters: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
};

const OPEN_VAULT_TOOL = {
  type: 'function',
  function: {
    name: 'openVault',
    description: 'Open a specific vault by ID and retrieve its contents.',
    parameters: {
      type: 'object',
      properties: {
        vaultId: {
          type: 'string',
          description: 'The ID of the vault to open.',
        },
      },
      required: ['vaultId'],
    },
  },
};

module.exports = { llmClient, MODEL, FLAG_VAULT_ID, VAULT_LIST, LIST_VAULTS_TOOL, OPEN_VAULT_TOOL };
