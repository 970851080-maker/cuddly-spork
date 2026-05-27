import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";
import fs from "node:fs/promises";

const baseDir = "C:/Users/admin/Desktop/个人";

const palette = {
  navy: "#1F4E79",
  blue: "#D9EAF7",
  green: "#E2F0D9",
  orange: "#FCE4D6",
  gray: "#F2F2F2",
  white: "#FFFFFF",
};

function styleTitle(range) {
  range.format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white, size: 16 },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
  };
}

function styleHeader(range) {
  range.format = {
    fill: palette.blue,
    font: { bold: true, color: "#000000" },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
    wrapText: true,
  };
}

function styleBody(range) {
  range.format = {
    verticalAlignment: "middle",
    wrapText: true,
  };
}

function setWidths(sheet, widths) {
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, 1, 1).format.columnWidthPx = width;
  });
}

async function exportWorkbook(workbook, path) {
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(path);
}

async function buildCashflow() {
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add("每月现金流");
  sheet.showGridLines = false;

  sheet.getRange("A1:D1").merge();
  sheet.getRange("A1").values = [["每月现金流表"]];
  styleTitle(sheet.getRange("A1:D1"));
  sheet.getRange("A2:D2").merge();
  sheet.getRange("A2").values = [["填写每月收入、支出和网贷，先保证不逾期，再安排学习投入。"]];
  sheet.getRange("A2:D2").format = { fill: palette.gray, font: { italic: true }, wrapText: true };

  sheet.getRange("A4:D4").values = [["项目", "金额", "备注", "分类"]];
  styleHeader(sheet.getRange("A4:D4"));
  sheet.getRange("A5:D14").values = [
    ["工资/项目收入", "", "填税后实际到账", "收入"],
    ["其他收入", "", "兼职、补贴、报销等", "收入"],
    ["房租/住宿", "", "如项目包住可填0", "固定支出"],
    ["吃饭交通", "", "按月估算", "生活支出"],
    ["手机/会员/日常", "", "能砍就砍", "生活支出"],
    ["网贷1还款", "", "平台/日期写备注", "债务"],
    ["网贷2还款", "", "平台/日期写备注", "债务"],
    ["网贷3还款", "", "平台/日期写备注", "债务"],
    ["最低生活费", "", "不能低于这个数", "底线"],
    ["每月剩余现金", "", "自动计算", "结果"],
  ];
  styleBody(sheet.getRange("A5:D14"));
  sheet.getRange("B14").formulas = [["=SUM(B5:B6)-SUM(B7:B13)"]];
  sheet.getRange("A16:D18").values = [
    ["判断", "剩余现金", "状态", "建议"],
    ["安全", ">2000", "相对安全", "可稳定备考"],
    ["高压", "0-500", "高压状态", "只保核心支出和一建不断线"],
  ];
  styleHeader(sheet.getRange("A16:D16"));
  styleBody(sheet.getRange("A17:D18"));
  sheet.getRange("A20:D20").merge();
  sheet.getRange("A20").values = [["提醒：债务、合同、证书、项目资料不要轻易删除；现金流先求稳。"]];
  sheet.getRange("A20:D20").format = { fill: palette.orange, font: { bold: true }, wrapText: true };

  sheet.getRange("B5:B14").format.numberFormat = "¥#,##0";
  setWidths(sheet, [150, 110, 260, 120]);
  sheet.freezePanes.freezeRows(4);
  await exportWorkbook(workbook, `${baseDir}/05_个人财务/每月现金流表.xlsx`);
}

async function buildExamCountdown() {
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add("一建倒计时");
  sheet.showGridLines = false;

  sheet.getRange("A1:E1").merge();
  sheet.getRange("A1").values = [["一建9月倒计时表"]];
  styleTitle(sheet.getRange("A1:E1"));
  sheet.getRange("A2:E2").merge();
  sheet.getRange("A2").values = [["主线：项目站稳 + 一建冲刺；项目忙时只保实务案例和错题。"]];
  sheet.getRange("A2:E2").format = { fill: palette.gray, font: { italic: true }, wrapText: true };

  sheet.getRange("A4:E4").values = [["阶段", "时间", "重点", "每日最低动作", "完成情况"]];
  styleHeader(sheet.getRange("A4:E4"));
  sheet.getRange("A5:E8").values = [
    ["基础阶段", "现在-6月底", "公共课快速过一遍，实务建立框架", "实务30分钟 + 公共课30分钟", ""],
    ["强化阶段", "7月", "实务案例专项，公共课刷真题", "案例1题 + 真题30题", ""],
    ["冲刺阶段", "8月", "高频考点、错题、模拟卷", "错题复盘 + 背诵清单", ""],
    ["考前阶段", "9月考前", "答题格式、重点回炉", "案例模板 + 错题回炉", ""],
  ];
  styleBody(sheet.getRange("A5:E8"));

  sheet.getRange("A10:E10").values = [["科目", "当前状态", "本周任务", "错题/薄弱点", "下一步"]];
  styleHeader(sheet.getRange("A10:E10"));
  sheet.getRange("A11:E14").values = [
    ["法规", "", "", "", ""],
    ["管理", "", "", "", ""],
    ["经济", "", "", "", ""],
    ["机电实务", "", "", "", "优先级最高"],
  ];
  styleBody(sheet.getRange("A11:E14"));

  sheet.getRange("A16:E16").merge();
  sheet.getRange("A16").values = [["提醒：今年核心策略不是把书看厚，而是公共课真题稳定、实务案例会答。"]];
  sheet.getRange("A16:E16").format = { fill: palette.orange, font: { bold: true }, wrapText: true };
  setWidths(sheet, [110, 120, 260, 220, 150]);
  sheet.freezePanes.freezeRows(4);
  await exportWorkbook(workbook, `${baseDir}/01_一建备考/一建9月倒计时表.xlsx`);
}

async function buildProjectChecklist() {
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add("入场清单");
  sheet.showGridLines = false;

  sheet.getRange("A1:D1").merge();
  sheet.getRange("A1").values = [["哈尔滨项目机电负责人入场清单"]];
  styleTitle(sheet.getRange("A1:D1"));
  sheet.getRange("A2:D2").merge();
  sheet.getRange("A2").values = [["前两周目标：摸清图纸、合同、人员、进度、材料、质量、安全、资料。"]];
  sheet.getRange("A2:D2").format = { fill: palette.gray, font: { italic: true }, wrapText: true };

  sheet.getRange("A4:D4").values = [["模块", "必须搞清楚", "输出物", "状态"]];
  styleHeader(sheet.getRange("A4:D4"));
  sheet.getRange("A5:D12").values = [
    ["图纸", "机电各专业图纸、冲突点", "图纸问题清单", ""],
    ["合同", "施工范围、甲供材、节点、签证规则", "合同要点表", ""],
    ["人员", "甲方、监理、总包、班组接口人", "联系人表", ""],
    ["进度", "土建进度、机电插入点、关键节点", "机电进度计划", ""],
    ["材料", "设备材料采购周期、到货风险", "材料计划表", ""],
    ["质量", "隐蔽、试压、绝缘、调试要求", "质量验收清单", ""],
    ["安全", "临电、动火、高处、交叉作业", "安全风险清单", ""],
    ["资料", "交底、方案、报验、会议纪要", "资料台账", ""],
  ];
  styleBody(sheet.getRange("A5:D12"));

  sheet.getRange("A14:D14").values = [["日期", "今天完成", "发现的问题/风险", "明天必须推进"]];
  styleHeader(sheet.getRange("A14:D14"));
  sheet.getRange("A15:D24").values = Array.from({ length: 10 }, () => ["", "", "", ""]);
  styleBody(sheet.getRange("A15:D24"));

  sheet.getRange("A26:D26").merge();
  sheet.getRange("A26").values = [["提醒：能形成签证、变更、会议纪要的事项，尽量留下书面记录。"]];
  sheet.getRange("A26:D26").format = { fill: palette.orange, font: { bold: true }, wrapText: true };
  setWidths(sheet, [100, 280, 190, 120]);
  sheet.freezePanes.freezeRows(4);
  await exportWorkbook(workbook, `${baseDir}/02_哈尔滨项目/哈尔滨项目机电负责人入场清单.xlsx`);
}

await fs.mkdir(`${baseDir}/01_一建备考`, { recursive: true });
await fs.mkdir(`${baseDir}/02_哈尔滨项目`, { recursive: true });
await fs.mkdir(`${baseDir}/05_个人财务`, { recursive: true });

await buildCashflow();
await buildExamCountdown();
await buildProjectChecklist();
