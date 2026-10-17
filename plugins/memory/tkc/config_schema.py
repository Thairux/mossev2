"""TKC memory provider config schema.

Fields are rendered by the generic memory-provider config panel
(``GET/PUT /api/memory/providers/{name}/config``). Non-secret fields are
persisted in config.yaml under ``memory.tkc``; secrets go to .env.
"""

from __future__ import annotations

from plugins.memory.config_schema import (
    KIND_TEXT,
    ProviderField,
    ProviderConfigSchema,
    STORAGE_FLAT_JSON,
)

CONFIG_SCHEMA = ProviderConfigSchema(
    name="tkc",
    label="TKC Memory (Token Cache Compressor)",
    storage=STORAGE_FLAT_JSON,
    docs_url="https://github.com/Thairux/tkc#readme",
    fields=(
        ProviderField(
            key="tkc_path",
            label="TKC CLI path",
            kind=KIND_TEXT,
            default="tkc",
            description="Path to the TKC CLI executable. Defaults to 'tkc' on PATH; set to a bundled TKC binary if vendoring TKC with mosse.",
            placeholder="tkc",
            env_key="TKC_PATH",
            inline=True,
        ),
        ProviderField(
            key="tkc_home",
            label="TKC home directory",
            kind=KIND_TEXT,
            default="",
            description="TKC home directory (where tkc.db lives). Defaults to ~/.tkc if unset.",
            placeholder="~/.tkc",
            env_key="TKC_HOME",
            inline=True,
        ),
    ),
)
