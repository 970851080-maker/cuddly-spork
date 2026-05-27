import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import fs from "node:fs/promises";

const files = [
  {
    path: "C:/Users/admin/Desktop/个人/05_个人财务/每月现金流表.xlsx",
    sheet: "每月现金流",
    range: "A1:D20",
  },
  {
    path: "C:/Users/admin/Desktop/个人/01_一建备考/一建9月倒计时表.xlsx",
    sheet: "一建倒计时",
    range: "A1:E16",
  },
  {
    path: "C:/Users/admin/Desktop/个人/02_哈尔滨项目/哈尔滨项目机电负责人入场清单.xlsx",
    sheet: "入场清单",
    range: "A1:D26",
  },
];

for (const item of files) {
  const input = await FileBlob.load(item.path);
  const workbook = await SpreadsheetFile.importXlsx(input);
  const summary = await workbook.inspect({
    kind: "table",
    range: `${item.sheet}!${item.range}`,
    include: "values,formulas",
    tableMaxRows: 8,
    tableMaxCols: 6,
    maxChars: 1600,
  });
  console.log(`OK inspect: ${item.path}`);
  console.log(summary.ndjson);

  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 20 },
    summary: "formula error scan",
  });
  console.log(`OK errors: ${errors.ndjson}`);

  const preview = await workbook.render({
    sheetName: item.sheet,
    range: item.range,
    scale: 1,
    format: "png",
  });
  const previewPath = item.path.replace(".xlsx", "_预览.png");
  await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
  console.log(`OK render: ${previewPath}`);
}
