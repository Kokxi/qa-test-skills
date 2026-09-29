// QA Test Skills Plugin
// 49个技能（含入口工作流 qa-test-skills + 48个专家级子技能）

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const skillsDir = join(__dirname, '..', 'skills');

/**
 * 获取所有可用的skills（含入口工作流 qa-test-skills）
 * 入口工作流已平级迁移到 skills/qa-test-skills/，由扫描自动发现
 */
export function getSkills() {
  const skills = [];
  
  if (!existsSync(skillsDir)) {
    return skills;
  }
  
  const skillDirs = readdirSync(skillsDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
  
  for (const skillName of skillDirs) {
    const skillFile = join(skillsDir, skillName, 'SKILL.md');
    if (existsSync(skillFile)) {
      try {
        const content = readFileSync(skillFile, 'utf-8');
        const metadata = parseSkillMetadata(content);
        skills.push({
          name: metadata.name || skillName,
          ...metadata,
          path: join(skillsDir, skillName)
        });
      } catch (error) {
        console.error(`Failed to load skill ${skillName}:`, error);
      }
    }
  }
  
  return skills;
}

/**
 * 解析 SKILL.md 的 YAML frontmatter
 * 支持两种标量写法：
 *   - 行内标量：  name: qa-xxx
 *   - 折叠/字面量块标量：description: >-
 *                         多行内容（缩进行）
 *
 * Agent Skills 规范只允许 6 个顶层字段（name/description/license/compatibility/
 * metadata/allowed-tools）。本技能集的自定义字段（when_to_use 等）全部收在
 * metadata 下，且 metadata 的值都是字符串，因此这里额外解析 metadata 一层，
 * 并把 when-to-use 映射回 when_to_use 以保持既有调用方不变。
 */
function parseSkillMetadata(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match) {
    return { description: '' };
  }

  const lines = match[1].replace(/\r\n/g, '\n').split('\n');
  const metadata = {};

  const readScalar = (lines, startIdx, rawValue) => {
    const inline = rawValue.trim();
    if (inline === '' || /^[>|][+-]?$/.test(inline)) {
      // 块标量（>- / > / |- / |）：收集后续缩进行，折叠为单行文本
      const parts = [];
      for (let j = startIdx + 1; j < lines.length; j++) {
        const line = lines[j];
        if (line.trim() === '') {
          parts.push('');
          continue;
        }
        if (!/^\s/.test(line)) break; // 遇到下一个顶层键，结束
        parts.push(line.trim());
      }
      return parts.join(' ').replace(/\s+/g, ' ').trim();
    }
    return inline.replace(/^["']|["']$/g, '').trim();
  };

  for (const field of ['name', 'description', 'license', 'allowed-tools']) {
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(new RegExp(`^${field}:[ \t]*(.*)$`));
      if (!m) continue;
      metadata[field] = readScalar(lines, i, m[1]);
      break;
    }
  }

  // metadata 一级子键（规范要求 string -> string；本技能集的复杂值是 JSON 字符串）
  const meta = {};
  let inMeta = false;
  for (const line of lines) {
    if (/^metadata:\s*/.test(line)) { inMeta = true; continue; }
    if (inMeta && /^\S/.test(line)) { inMeta = false; }   // 回到顶层
    if (!inMeta) continue;
    const m = line.match(/^\s+([A-Za-z0-9_-]+):\s*(.*)$/);
    if (m) meta[m[1]] = unwrapMetaValue(m[2].trim());
  }
  metadata.metadata = meta;
  // 兼容既有调用方：when_to_use -> metadata['when-to-use']
  if (meta['when-to-use']) metadata.when_to_use = meta['when-to-use'];
  if (meta['display-name']) metadata.displayName = meta['display-name'];
  if (meta.version) metadata.version = meta.version;

  return metadata;
}

/**
 * 解析 metadata 的标量值。规范要求 metadata 为 string -> string，本技能集的写法是：
 *   - 标量：  version: "1.7.9"                → JSON 引号包裹的裸文本
 *   - 复杂值：references: "[\"a.md\"]"        → 双引号包裹的紧凑 JSON
 * 做法是先把整个标量当 JSON 解析（剥掉 YAML 双引号并还原转义），
 * 若解析出的字符串本身又是合法 JSON（数组/对象），再解析一层。
 */
function unwrapMetaValue(raw) {
  if (typeof raw !== 'string' || raw.length === 0) return raw;
  let inner = raw;
  if (inner.startsWith('"')) {
    try {
      inner = JSON.parse(inner);          // 还原 \" 与 \n 等转义
    } catch {
      inner = inner.slice(1, -1);
    }
  } else if (inner.startsWith("'")) {
    inner = inner.slice(1, -1);
  }
  if (typeof inner !== 'string') return inner;
  const t = inner.trim();
  if (t.startsWith('[') || t.startsWith('{')) {
    try {
      return JSON.parse(t);
    } catch {
      return inner;
    }
  }
  return inner;
}

/**
 * 获取指定skill的内容（按 skills/ 下目录查找）
 */
export function getSkillContent(skillName) {
  const skillFile = join(skillsDir, skillName, 'SKILL.md');
  if (existsSync(skillFile)) {
    return readFileSync(skillFile, 'utf-8');
  }
  return null;
}

/**
 * 获取所有skill名称
 */
export function getSkillNames() {
  return getSkills().map(s => s.name);
}

// 默认导出
export default {
  getSkills,
  getSkillContent,
  getSkillNames
};