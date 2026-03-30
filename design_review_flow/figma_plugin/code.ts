// Flaw Injector Plugin — applies flaw specs to Figma designs

interface Flaw {
  id: string;
  screen: string;
  type: string;
  severity: string;
  instruction: string;
  target_layer: string;
  rationale: string;
}

interface FlawSpec {
  source_file: string;
  target_screens: string[];
  flaws: Flaw[];
  answer_key: {
    flaws_summary: string;
    expected_findings: string[];
    overall_quality: string;
  };
}

interface ApplyResult {
  flaw_id: string;
  status: "applied" | "needs_manual" | "error";
  message: string;
}

// Show the UI
figma.showUI(__html__, { width: 500, height: 600 });

// Listen for messages from the UI
figma.ui.onmessage = async (msg: { type: string; spec?: string }) => {
  if (msg.type === "preview") {
    await handlePreview(msg.spec || "");
  } else if (msg.type === "apply") {
    await handleApply(msg.spec || "");
  } else if (msg.type === "cancel") {
    figma.closePlugin();
  }
};

async function handlePreview(specJson: string) {
  try {
    const spec: FlawSpec = JSON.parse(specJson);
    const results: Array<{ flaw_id: string; found: boolean; layer_name: string }> = [];

    for (const flaw of spec.flaws) {
      const node = findNodeByName(flaw.target_layer);
      results.push({
        flaw_id: flaw.id,
        found: node !== null,
        layer_name: flaw.target_layer,
      });
    }

    figma.ui.postMessage({ type: "preview-result", results });
  } catch (e) {
    figma.ui.postMessage({
      type: "error",
      message: `Failed to parse spec: ${(e as Error).message}`,
    });
  }
}

async function handleApply(specJson: string) {
  try {
    const spec: FlawSpec = JSON.parse(specJson);
    const results: ApplyResult[] = [];

    for (const flaw of spec.flaws) {
      const result = await applyFlaw(flaw);
      results.push(result);
    }

    figma.ui.postMessage({ type: "apply-result", results });
    figma.notify(
      `Done: ${results.filter((r) => r.status === "applied").length} applied, ` +
      `${results.filter((r) => r.status === "needs_manual").length} need manual action`
    );
  } catch (e) {
    figma.ui.postMessage({
      type: "error",
      message: `Failed to apply: ${(e as Error).message}`,
    });
  }
}

function findNodeByName(name: string): SceneNode | null {
  // Search the entire document for a node with the exact name
  // v1: exact match only — no fuzzy matching per spec
  const allNodes = figma.currentPage.findAll();

  for (const node of allNodes) {
    if (node.name === name) {
      return node;
    }
  }

  return null;
}

async function applyFlaw(flaw: Flaw): Promise<ApplyResult> {
  const node = findNodeByName(flaw.target_layer);

  if (!node) {
    return {
      flaw_id: flaw.id,
      status: "needs_manual",
      message: `Layer not found: "${flaw.target_layer}"`,
    };
  }

  try {
    const instruction = flaw.instruction.toLowerCase();

    // Text content changes
    if (node.type === "TEXT" && hasTextChange(instruction)) {
      await applyTextChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Text changed on "${node.name}"` };
    }

    // Color/fill changes
    if (hasColorChange(instruction)) {
      applyColorChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Color changed on "${node.name}"` };
    }

    // Size changes
    if (hasSizeChange(instruction)) {
      applySizeChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Size changed on "${node.name}"` };
    }

    // Font changes
    if (node.type === "TEXT" && hasFontChange(instruction)) {
      await applyFontChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Font changed on "${node.name}"` };
    }

    // If we can't determine the change type, mark as manual
    return {
      flaw_id: flaw.id,
      status: "needs_manual",
      message: `Found layer "${node.name}" but couldn't auto-apply: "${flaw.instruction}"`,
    };
  } catch (e) {
    return {
      flaw_id: flaw.id,
      status: "error",
      message: `Error applying to "${node.name}": ${(e as Error).message}`,
    };
  }
}

// ─── Change Detection Helpers ───

function hasTextChange(instruction: string): boolean {
  return /change text|change .* to|rename|update text|text from .* to/i.test(instruction);
}

function hasColorChange(instruction: string): boolean {
  return /#[0-9a-fA-F]{6}|color|fill|background/i.test(instruction);
}

function hasSizeChange(instruction: string): boolean {
  return /size|resize|reduce .* size|increase .* size|width|height|smaller|larger/i.test(instruction);
}

function hasFontChange(instruction: string): boolean {
  return /font.?size|font.?weight|bold|regular|light/i.test(instruction);
}

// ─── Change Application Helpers ───

async function applyTextChange(node: TextNode, instruction: string): Promise<void> {
  // Extract "to 'X'" or "to \"X\"" pattern
  const toMatch = instruction.match(/(?:to|with)\s+['"]([^'"]+)['"]/i);
  if (toMatch) {
    await figma.loadFontAsync(node.fontName as FontName);
    node.characters = toMatch[1];
    return;
  }

  // Extract "from 'X' to 'Y'" pattern
  const fromToMatch = instruction.match(/from\s+['"]([^'"]+)['"]\s+to\s+['"]([^'"]+)['"]/i);
  if (fromToMatch) {
    await figma.loadFontAsync(node.fontName as FontName);
    node.characters = fromToMatch[2];
    return;
  }
}

function applyColorChange(node: SceneNode, instruction: string): void {
  const hexMatch = instruction.match(/#([0-9a-fA-F]{6})/);
  if (!hexMatch) return;

  const hex = hexMatch[1];
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  if ("fills" in node) {
    node.fills = [{ type: "SOLID", color: { r, g, b } }];
  }
}

function applySizeChange(node: SceneNode, instruction: string): void {
  if (!("resize" in node)) return;

  // Try to extract specific dimensions
  const widthMatch = instruction.match(/width\s*(?:to\s*)?(\d+)/i);
  const heightMatch = instruction.match(/height\s*(?:to\s*)?(\d+)/i);

  if (widthMatch || heightMatch) {
    const newWidth = widthMatch ? parseInt(widthMatch[1]) : node.width;
    const newHeight = heightMatch ? parseInt(heightMatch[1]) : node.height;
    node.resize(newWidth, newHeight);
    return;
  }

  // Handle "reduce size to match" or percentage-based
  if (/reduce|smaller|decrease/i.test(instruction)) {
    node.resize(node.width * 0.7, node.height * 0.7);
  } else if (/increase|larger|bigger/i.test(instruction)) {
    node.resize(node.width * 1.3, node.height * 1.3);
  }
}

async function applyFontChange(node: TextNode, instruction: string): Promise<void> {
  const currentFont = node.fontName as FontName;
  await figma.loadFontAsync(currentFont);

  // Font size changes
  const sizeMatch = instruction.match(/font.?size\s*(?:to\s*)?(\d+)/i);
  if (sizeMatch) {
    node.fontSize = parseInt(sizeMatch[1]);
    return;
  }

  // Font weight changes
  if (/bold/i.test(instruction)) {
    try {
      const boldFont: FontName = { family: currentFont.family, style: "Bold" };
      await figma.loadFontAsync(boldFont);
      node.fontName = boldFont;
    } catch {
      // Bold variant not available
    }
  } else if (/regular|normal/i.test(instruction)) {
    try {
      const regularFont: FontName = { family: currentFont.family, style: "Regular" };
      await figma.loadFontAsync(regularFont);
      node.fontName = regularFont;
    } catch {
      // Regular variant not available
    }
  }
}
