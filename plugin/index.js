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
 * 解析SKILL.md的YAML frontmatter
 * 支持两种标量写法：
 *   - 行内标量：  name: qa-xxx
 *   - 折叠/字面量块标量：description: >-
 *                         多行内容（缩进行）
 */
function parseSkillMetadata(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match) {
    return { description: '' };
  }

  const lines = match[1].replace(/\r\n/g, '\n').split('\n');
  const metadata = {};

  const fields = ['name', 'description', 'when_to_use'];
  for (const field of fields) {
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(new RegExp(`^${field}:\\s*(.*)$`));
      if (!m) continue;
      const inline = m[1].trim();
      if (inline === '' || /^[>|][+-]?$/.test(inline)) {
        // 块标量（>- / > / |- / |）：收集后续缩进行，折叠为单行文本
        const parts = [];
        for (let j = i + 1; j < lines.length; j++) {
          const line = lines[j];
          if (line.trim() === '') {
            parts.push('');
            continue;
          }
          if (!/^\s/.test(line)) break; // 遇到下一个顶层键，结束
          parts.push(line.trim());
        }
        metadata[field] = parts.join(' ').replace(/\s+/g, ' ').trim();
      } else {
        metadata[field] = inline.replace(/^["']|["']$/g, '').trim();
      }
      break;
    }
  }

  return metadata;
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