# Tools

## build_prompt_packets.py

Generates a markdown file with ready-to-paste GPT prompts for each lead in your CRM CSV.

### Command

```bash
python client-acquisition-engine/tools/build_prompt_packets.py --input "<path-to-leads.csv>" --output "client-acquisition-engine/tools/prompt_packets.md"
```

### Typical Workflow

1. Export your `Leads` sheet as CSV.
2. Run the script.
3. Open generated `prompt_packets.md`.
4. Paste prompts into GPT and copy outputs back into CRM fields.
