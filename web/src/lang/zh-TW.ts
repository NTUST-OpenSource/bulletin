// All UI copy. The repository is English; this file is exempt (AGENTS.md).
export const brand = {
  home: "bulletin 首頁",
} as const;

export const header = {
  search: "搜尋",
  settings: "設定",
} as const;

export const stream = {
  filters: "篩選",
  allUnits: "所有單位",
  allTopics: "全部",
  reorder: "調整標籤順序",
  withdrawn: "已刪除",
  nothingFollowed: "還沒有關注的單位",
  pickUnits: "選擇單位",
  nothingFound: "沒有符合的公告",
  clearFilters: "清除篩選",
  loading: "載入中",
} as const;

export const article = {
  close: "關閉",
  more: "更多",
  showRewrite: "顯示改寫",
  showSchool: "顯示原文",
  withdrawn: "已刪除",
} as const;

export const preview = {
  download: "下載",
  previous: "上一張",
  next: "下一張",
  zoomIn: "放大",
  zoomOut: "縮小",
  failed: "無法預覽這個檔案",
  school: "開啟學校的檔案",
} as const;

const WEEKDAYS = "日一二三四五六";

export const days = {
  today: "今天",
  yesterday: "昨天",
  weekday: (day: number) => `週${WEEKDAYS[day]}`,
  month: (month: number, year: number | null) => (year ? `${year}年${month}月` : `${month}月`),
  date: (month: number, date: number, year: number | null) => `${year ? `${year}年` : ""}${month}月${date}日`,
} as const;

export const settings = {
  title: "設定",
  close: "關閉",
  back: "返回",
  appearance: "外觀",
  themes: { system: "跟隨系統", light: "淺色", dark: "深色" },
  display: "預設顯示",
  prefers: { rendition: "改寫", raw: "原文" },
  units: "關注的單位",
  edit: "編輯",
  hidden: "隱藏的公告板",
  show: "顯示",
  topics: "標籤順序",
  adjust: "調整",
  move: (topic: string) => `移動「${topic}」`,
  export: "匯出",
  copyJson: "複製設定",
  download: "下載 JSON",
  copyLink: "複製分享連結",
  import: "匯入",
  importLabel: "設定 JSON 或分享連結",
  importPlaceholder: "貼上設定 JSON 或分享連結",
  chooseFile: "選擇檔案",
  unreadablePaste: "無法讀取：請貼上本站匯出的設定或分享連結。",
  unreadableFile: "無法讀取：檔案不是本站匯出的設定。",
  reset: "清除所有設定",
  resetAsk: {
    title: "清除所有設定？",
    text: "關注的單位、隱藏的公告板、標籤順序與外觀都會恢復預設。",
    yes: "清除",
    no: "取消",
  },
  note: "內容轉寫自國立臺灣科技大學各單位網站，以原網頁內容為準",
} as const;

export const onboarding = {
  department: "你在哪個系所？",
  others: "還想看哪些單位的公告？",
  skip: "略過",
  next: "下一步",
  back: "上一步",
  done: "開始使用",
} as const;

export const menu = {
  hide: (board: string) => `隱藏「${board}」`,
  unfollow: (unit: string) => `不再關注「${unit}」`,
  follow: (unit: string) => `關注「${unit}」`,
  copyLink: "複製連結",
  openSchool: "開啟原網頁",
  hidden: (board: string) => `已隱藏「${board}」`,
  unfollowed: (unit: string) => `已取消關注「${unit}」`,
  followed: (unit: string) => `已關注「${unit}」`,
  copied: "已複製連結",
  undo: "復原",
} as const;

export const transfer = {
  copiedJson: "已複製設定",
  copiedLink: "已複製分享連結",
  noClipboard: "無法存取剪貼簿",
  linkApplied: "已套用分享的設定",
  imported: "已匯入設定",
  overwritten: "已覆蓋設定",
  overwrite: {
    title: "覆蓋目前的設定？",
    text: "匯入的設定會取代你目前所有的設定。",
    yes: "覆蓋",
    no: "保留目前設定",
  },
} as const;

export const units = {
  search: "搜尋單位",
  none: "沒有符合的單位",
  school: "全校與行政單位",
  other: "其他",
} as const;
