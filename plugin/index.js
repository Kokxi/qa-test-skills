// QA Test Skills Plugin
// 48个专家级测试技能集合

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const skillsDir = join(__dirname, '..', 'skills');

/**
 * 获取所有可用的skills
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
          name: skillName,
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
 */
function parseSkillMetadata(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match) {
    return { description: '' };
  }
  
  const yaml = match[1];
  const metadata = {};
  
  // 解析简单的YAML字段
  const fields = ['name', 'description', 'when_to_use'];
  for (const field of fields) {
    const fieldMatch = yaml.match(new RegExp(`${field}:\\s*(.+)`));
    if (fieldMatch) {
      metadata[field] = fieldMatch[1].trim();
    }
  }
  
  return metadata;
}

/**
 * 获取指定skill的内容
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