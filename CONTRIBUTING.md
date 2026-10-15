# Contributing to ToolDrop

Thank you for your interest in contributing to ToolDrop! This guide explains how to add new AI tools to the directory.

## Adding a New Tool

All tools are stored in a single JSON file: `src/_data/tools.json`

### Tool Entry Format

Each tool entry follows this structure:

```json
{
  "name": "Tool Name",
  "url": "https://official-website.com",
  "description": "A short description of what the tool does (1-2 sentences).",
  "categories": ["Category 1", "Category 2"],
  "pricing": "free | freemium | paid",
  "pricingNote": "Free tier, Pro from $X/mo",
  "tags": ["tag1", "tag2", "tag3"],
  "dateAdded": "YYYY-MM-DD",
  "newRelease": true,
  "featured": true
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Official name of the tool |
| `url` | Yes | Official website URL (must be valid and accessible) |
| `description` | Yes | Short description (1-2 sentences, ~100-150 characters) |
| `categories` | Yes | Array of categories (see list below) |
| `pricing` | Yes | One of: `free`, `freemium`, `paid` |
| `pricingNote` | No | Human-readable pricing info (e.g., "From $10/mo") |
| `tags` | Yes | Array of relevant keywords/features |
| `dateAdded` | Yes | Date added in YYYY-MM-DD format |
| `newRelease` | No | Set to `true` to feature in "New Releases" |
| `featured` | No | Set to `true` to show in featured section |

### Available Categories

- `AI Coding Agents & IDEs`
- `App Builders`
- `Code Review & Testing`
- `Game Art & Sprites`
- `3D & Models`
- `Audio, Music & SFX`
- `Voice`
- `Game Design & Narrative`
- `Video & Trailers`
- `Marketing & Store Page Copy`
- `Agent Frameworks`

### Example: Adding a Tool

1. Open `src/_data/tools.json`
2. Add your tool entry at the end of the array (before the closing `]`)
3. Fill in all required fields
4. Verify the URL works and pricing is accurate

```json
{
  "name": "NewAITool",
  "url": "https://newaitool.com",
  "description": "AI tool that helps with X and Y for game developers.",
  "categories": ["Game Art & Sprites"],
  "pricing": "freemium",
  "pricingNote": "Free tier, Pro from $15/mo",
  "tags": ["game assets", "AI art", "sprites"],
  "dateAdded": "2024-10-15",
  "newRelease": true
}
```

## Guidelines

### Do
- Only add tools that currently exist and are accessible
- Verify the official URL is correct
- Use accurate pricing information
- Write clear, concise descriptions
- Add relevant tags for searchability

### Don't
- Don't invent or guess pricing - leave `pricingNote` empty if unknown
- Don't add tools without verifying they exist
- Don't use affiliate links
- Don't add duplicate tools

## Building Locally

```bash
# Install dependencies
npm install

# Run development server
npm run serve

# Build for production
npm run build
```

## Pull Request Process

1. Fork the repository
2. Create a branch for your changes
3. Add your tool(s) to `src/_data/tools.json`
4. Test locally with `npm run serve`
5. Submit a pull request with:
   - Tool name(s) added
   - Brief justification for why it belongs

## Questions?

Open an issue on GitHub if you have questions or suggestions for improving the directory.
