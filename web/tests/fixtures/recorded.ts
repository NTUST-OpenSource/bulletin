// Recorded from https://bulletin.ntust.org/api/v1 on 2026-11-15 by scripts/record-fixtures.ts.
import type { Article, Dimension, Page, Site } from "../../src/lib/api.ts";

export const sites = [
  {
    "id": 1045,
    "host": "bulletin.ntust.edu.tw",
    "unit": "全校公佈欄",
    "kind": "all",
    "college": null,
    "boards": [
      {
        "key": "1045-1391",
        "name": "公佈欄",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1000,
    "host": "www.ntust.edu.tw",
    "unit": "官網",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1000-167",
        "name": "新聞專區/校園新聞/媒體報導",
        "category": "news"
      },
      {
        "key": "1000-168",
        "name": "公布欄",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1063,
    "host": "www.secretariat.ntust.edu.tw",
    "unit": "秘書室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1063-2",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1063-1784",
        "name": "簡報/校景圖檔參考格式",
        "category": "announcement"
      },
      {
        "key": "1063-1785",
        "name": "Taiwan Tech 標準字型",
        "category": "announcement"
      },
      {
        "key": "1063-1786",
        "name": "名片參考格式",
        "category": "announcement"
      },
      {
        "key": "1063-1787",
        "name": "電子賀卡",
        "category": "announcement"
      },
      {
        "key": "1063-2043",
        "name": "圖書館管理",
        "category": "announcement"
      },
      {
        "key": "1063-2046",
        "name": "著作權宣導",
        "category": "announcement"
      },
      {
        "key": "1063-2138",
        "name": "本校性別相關法規",
        "category": "regulation"
      },
      {
        "key": "1063-2139",
        "name": "相關作業流程",
        "category": "announcement"
      },
      {
        "key": "1063-2140",
        "name": "年度成果報告與工作計畫",
        "category": "news"
      },
      {
        "key": "1063-2141",
        "name": "各項申請表格下載",
        "category": "regulation"
      },
      {
        "key": "1063-2144",
        "name": "校園性別事件防治微電影",
        "category": "announcement"
      },
      {
        "key": "1063-2147",
        "name": "性平會文宣",
        "category": "announcement"
      },
      {
        "key": "1063-2148",
        "name": "政府相關法規",
        "category": "regulation"
      },
      {
        "key": "1063-2149",
        "name": "公告訊息",
        "category": "announcement"
      },
      {
        "key": "1063-2175",
        "name": "秘書室公告訊息",
        "category": "announcement"
      },
      {
        "key": "1063-2185",
        "name": "評鑑最新消息",
        "category": "announcement"
      },
      {
        "key": "1063-2211",
        "name": "公關組最新消息",
        "category": "announcement"
      },
      {
        "key": "1063-2212",
        "name": "臺科大新聞",
        "category": "news"
      },
      {
        "key": "1063-2215",
        "name": "公關表單下載",
        "category": "regulation"
      },
      {
        "key": "1063-2216",
        "name": "常見問題",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1048,
    "host": "www.academic.ntust.edu.tw",
    "unit": "教務處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1048-1405",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1048-1407",
        "name": "線上申請",
        "category": "announcement"
      },
      {
        "key": "1048-1413",
        "name": "處本部公告",
        "category": "announcement"
      },
      {
        "key": "1048-1414",
        "name": "研教組公告",
        "category": "announcement"
      },
      {
        "key": "1048-1415",
        "name": "註冊組公告",
        "category": "announcement"
      },
      {
        "key": "1048-1416",
        "name": "課務組公告",
        "category": "announcement"
      },
      {
        "key": "1048-1417",
        "name": "綜合業務組公告",
        "category": "announcement"
      },
      {
        "key": "1048-1986",
        "name": "雙主修、輔系 最新消息",
        "category": "announcement"
      },
      {
        "key": "1048-2076",
        "name": "新聞專區",
        "category": "news"
      }
    ]
  },
  {
    "id": 1053,
    "host": "student.ntust.edu.tw",
    "unit": "學生事務處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1053-1435",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1053-1436",
        "name": "學生宿舍公告",
        "category": "announcement"
      },
      {
        "key": "1053-1437",
        "name": "助學措施",
        "category": "announcement"
      },
      {
        "key": "1053-1439",
        "name": "生輔組",
        "category": "announcement"
      },
      {
        "key": "1053-1440",
        "name": "活動組",
        "category": "announcement"
      },
      {
        "key": "1053-1441",
        "name": "就輔組",
        "category": "announcement"
      },
      {
        "key": "1053-1442",
        "name": "諮輔組",
        "category": "announcement"
      },
      {
        "key": "1053-1443",
        "name": "資源教室",
        "category": "announcement"
      },
      {
        "key": "1053-1444",
        "name": "衛保組",
        "category": "announcement"
      },
      {
        "key": "1053-1446",
        "name": "社團活動",
        "category": "announcement"
      },
      {
        "key": "1053-1676",
        "name": "宿舍收費標準及法規",
        "category": "regulation"
      },
      {
        "key": "1053-1678",
        "name": "兵役相關連結",
        "category": "announcement"
      },
      {
        "key": "1053-1691",
        "name": "不利處境助學金(原弱勢助學金)相關法規",
        "category": "regulation"
      },
      {
        "key": "1053-1692",
        "name": "生活助學金法規",
        "category": "regulation"
      },
      {
        "key": "1053-1715",
        "name": "急難申請-臺科大急難就學補助",
        "category": "announcement"
      },
      {
        "key": "1053-1716",
        "name": "急難申請-教育部學產基金",
        "category": "announcement"
      },
      {
        "key": "1053-1780",
        "name": "畢業生專區",
        "category": "announcement"
      },
      {
        "key": "1053-2450",
        "name": "社團外部補助資源專區",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1054,
    "host": "www.general.ntust.edu.tw",
    "unit": "總務處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1054-5",
        "name": "總務處公告事項",
        "category": "announcement"
      },
      {
        "key": "1054-6",
        "name": "文書組最新消息",
        "category": "announcement"
      },
      {
        "key": "1054-7",
        "name": "事務組最新消息",
        "category": "announcement"
      },
      {
        "key": "1054-8",
        "name": "營繕組最新消息",
        "category": "announcement"
      },
      {
        "key": "1054-9",
        "name": "保管組最新消息",
        "category": "announcement"
      },
      {
        "key": "1054-10",
        "name": "出納組最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1055,
    "host": "www.rd.ntust.edu.tw",
    "unit": "研究發展處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1055-19",
        "name": "計服公告",
        "category": "announcement"
      },
      {
        "key": "1055-1604",
        "name": "跨校學術合作徵求",
        "category": "announcement"
      },
      {
        "key": "1055-2457",
        "name": "跨校學術合作徵求 (置頂）",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1060,
    "host": "www.oia.ntust.edu.tw",
    "unit": "國際事務處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1060-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1060-364",
        "name": "OIA公告",
        "category": "announcement"
      },
      {
        "key": "1060-1588",
        "name": "校外獎學金",
        "category": "announcement"
      },
      {
        "key": "1060-2339",
        "name": "OIA新聞",
        "category": "news"
      }
    ]
  },
  {
    "id": 1061,
    "host": "iac.ntust.edu.tw",
    "unit": "產學營運處",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1061-1147",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1061-1689",
        "name": "最新消息（分類）",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1067,
    "host": "www.accounting.ntust.edu.tw",
    "unit": "主計室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1067-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1067-6",
        "name": "公告事項",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1066,
    "host": "www.personnel.ntust.edu.tw",
    "unit": "人事室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1066-1",
        "name": "最新消息(非置頂請放此)",
        "category": "announcement"
      },
      {
        "key": "1066-5",
        "name": "公告",
        "category": "announcement"
      },
      {
        "key": "1066-7",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1068,
    "host": "she.ntust.edu.tw",
    "unit": "環安室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1068-1496",
        "name": "化學品公告",
        "category": "announcement"
      },
      {
        "key": "1068-1497",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1068-2345",
        "name": "實驗室廢棄物公告",
        "category": "announcement"
      },
      {
        "key": "1068-2347",
        "name": "健康活動宣導公告",
        "category": "announcement"
      },
      {
        "key": "1068-2348",
        "name": "教育訓練公告",
        "category": "announcement"
      },
      {
        "key": "1068-2349",
        "name": "公共空間公告",
        "category": "announcement"
      },
      {
        "key": "1068-2350",
        "name": "實驗室公告",
        "category": "announcement"
      },
      {
        "key": "1068-2351",
        "name": "實驗室廢棄物校內規定",
        "category": "regulation"
      },
      {
        "key": "1068-2352",
        "name": "一般廢棄物及資源回收宣導",
        "category": "announcement"
      },
      {
        "key": "1068-2354",
        "name": "新進人員安衛教育訓練",
        "category": "announcement"
      },
      {
        "key": "1068-2355",
        "name": "教育訓練報告",
        "category": "announcement"
      },
      {
        "key": "1068-2357",
        "name": "教育訓練紀錄",
        "category": "announcement"
      },
      {
        "key": "1068-2358",
        "name": "意外事故/職災通報表單",
        "category": "regulation"
      },
      {
        "key": "1068-2364",
        "name": "化學品校內規定",
        "category": "regulation"
      },
      {
        "key": "1068-2365",
        "name": "化學品校外法規",
        "category": "regulation"
      },
      {
        "key": "1068-2373",
        "name": "緊急應變公告",
        "category": "announcement"
      },
      {
        "key": "1068-2374",
        "name": "緊急應變校內規定",
        "category": "regulation"
      },
      {
        "key": "1068-2377",
        "name": "緊急應變資訊",
        "category": "regulation"
      },
      {
        "key": "1068-2378",
        "name": "生物安全公告",
        "category": "announcement"
      },
      {
        "key": "1068-2379",
        "name": "生物安全校內規定",
        "category": "regulation"
      },
      {
        "key": "1068-2380",
        "name": "生物安全校外法規",
        "category": "regulation"
      },
      {
        "key": "1068-2383",
        "name": "游離輻射公告",
        "category": "announcement"
      },
      {
        "key": "1068-2388",
        "name": "綠色採購公告",
        "category": "announcement"
      },
      {
        "key": "1068-2389",
        "name": "綠色採購校內規定",
        "category": "regulation"
      },
      {
        "key": "1068-2390",
        "name": "綠色採購校外法規",
        "category": "regulation"
      },
      {
        "key": "1068-2391",
        "name": "綠色採購報告",
        "category": "announcement"
      },
      {
        "key": "1068-2393",
        "name": "減塑專區公告",
        "category": "announcement"
      },
      {
        "key": "1068-2408",
        "name": "健康資訊公告",
        "category": "announcement"
      },
      {
        "key": "1068-2409",
        "name": "新進人員體格檢查",
        "category": "announcement"
      },
      {
        "key": "1068-2410",
        "name": "在職人員一般健康檢查",
        "category": "announcement"
      },
      {
        "key": "1068-2411",
        "name": "特殊健康檢查",
        "category": "announcement"
      },
      {
        "key": "1068-2412",
        "name": "其他",
        "category": "announcement"
      },
      {
        "key": "1068-2413",
        "name": "健康文宣",
        "category": "announcement"
      },
      {
        "key": "1068-2420",
        "name": "在職人員安衛教育訓練",
        "category": "announcement"
      },
      {
        "key": "1068-2421",
        "name": "環境教育規定",
        "category": "regulation"
      },
      {
        "key": "1068-2422",
        "name": "毒性及關注化學物質(環境部)",
        "category": "announcement"
      },
      {
        "key": "1068-2423",
        "name": "新化學物質(環境部)",
        "category": "announcement"
      },
      {
        "key": "1068-2424",
        "name": "先驅化學品(經濟部)",
        "category": "announcement"
      },
      {
        "key": "1068-2425",
        "name": "優先化學品(勞動部)",
        "category": "announcement"
      },
      {
        "key": "1068-2426",
        "name": "管制性化學品(勞動部)",
        "category": "announcement"
      },
      {
        "key": "1068-2427",
        "name": "化學品分級管理(勞動部)",
        "category": "announcement"
      },
      {
        "key": "1068-2428",
        "name": "事業用爆炸物(經濟部)",
        "category": "announcement"
      },
      {
        "key": "1068-2429",
        "name": "消防演練",
        "category": "announcement"
      },
      {
        "key": "1068-2431",
        "name": "實驗室規定",
        "category": "regulation"
      },
      {
        "key": "1068-2454",
        "name": "消防公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1069,
    "host": "www.sport.ntust.edu.tw",
    "unit": "體育室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1069-1475",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1049,
    "host": "library.ntust.edu.tw",
    "unit": "圖書館",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1049-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1049-203",
        "name": "閱覽服務",
        "category": "announcement"
      },
      {
        "key": "1049-204",
        "name": "參考諮詢服務",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1070,
    "host": "lc.ntust.edu.tw",
    "unit": "語言中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1070-1050",
        "name": "活動公告",
        "category": "announcement"
      },
      {
        "key": "1070-1051",
        "name": "榮譽榜單",
        "category": "news"
      },
      {
        "key": "1070-1053",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1070-1626",
        "name": "徵才公告",
        "category": "announcement"
      },
      {
        "key": "1070-1627",
        "name": "抵免與獎勵公告",
        "category": "announcement"
      },
      {
        "key": "1070-1628",
        "name": "新生相關公告",
        "category": "announcement"
      },
      {
        "key": "1070-1828",
        "name": "英文單字",
        "category": "news"
      },
      {
        "key": "1070-1829",
        "name": "校外公文",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1050,
    "host": "www.cc.ntust.edu.tw",
    "unit": "電子計算機中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1050-1426",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1059,
    "host": "po.ntust.edu.tw",
    "unit": "永續發展與校務研究中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1059-763",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1051,
    "host": "ctld.ntust.edu.tw",
    "unit": "教學發展中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1051-1873",
        "name": "校內講座研習",
        "category": "announcement"
      },
      {
        "key": "1051-1891",
        "name": "各類申請公告",
        "category": "announcement"
      },
      {
        "key": "1051-2015",
        "name": "教學實踐研究計畫公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1116,
    "host": "uptp-office.ntust.edu.tw",
    "unit": "臺巴計畫辦公室",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1116-2155",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1116-2156",
        "name": "活動資訊",
        "category": "regulation"
      }
    ]
  },
  {
    "id": 1108,
    "host": "indigenous.ntust.edu.tw",
    "unit": "原住民族學生資源中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1108-1929",
        "name": "最新消息（總表）",
        "category": "announcement"
      },
      {
        "key": "1108-2021",
        "name": "文化傳遞專案",
        "category": "announcement"
      },
      {
        "key": "1108-2031",
        "name": "校內最新消息",
        "category": "announcement"
      },
      {
        "key": "1108-2050",
        "name": "大專原住民族音樂大賽",
        "category": "announcement"
      },
      {
        "key": "1108-2052",
        "name": "校外轉知",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1052,
    "host": "www.admission.ntust.edu.tw",
    "unit": "招生資訊",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1052-1536",
        "name": "研究所招生公告",
        "category": "announcement"
      },
      {
        "key": "1052-1537",
        "name": "大學部招生公告",
        "category": "announcement"
      },
      {
        "key": "1052-1538",
        "name": "最新招生公告(全部)",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1076,
    "host": "cla.ntust.edu.tw",
    "unit": "通識教育中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1076-1476",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1076-1477",
        "name": "校外資訊",
        "category": "regulation"
      },
      {
        "key": "1076-1541",
        "name": "B向度",
        "category": "course"
      },
      {
        "key": "1076-1542",
        "name": "C向度",
        "category": "course"
      },
      {
        "key": "1076-1543",
        "name": "D向度",
        "category": "course"
      },
      {
        "key": "1076-1544",
        "name": "E向度",
        "category": "course"
      },
      {
        "key": "1076-1545",
        "name": "F向度",
        "category": "course"
      },
      {
        "key": "1076-1546",
        "name": "表單與連結>學生>",
        "category": "regulation"
      },
      {
        "key": "1076-1942",
        "name": "活動紀錄",
        "category": "news"
      },
      {
        "key": "1076-1949",
        "name": "通識抵萬金最新公告",
        "category": "announcement"
      },
      {
        "key": "1076-2173",
        "name": "英語通識課程認列",
        "category": "announcement"
      },
      {
        "key": "1076-2252",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1076-2282",
        "name": "社會實踐博雅通識活動資訊",
        "category": "regulation"
      },
      {
        "key": "1076-2312",
        "name": "跨域活動交流｜Talks, Tours & Workshops",
        "category": "announcement"
      },
      {
        "key": "1076-2313",
        "name": "校園策展計畫｜Campus Curation",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1040,
    "host": "www.tec.ntust.edu.tw",
    "unit": "師資培育中心",
    "kind": "admin",
    "college": null,
    "boards": [
      {
        "key": "1040-514",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1040-649",
        "name": "招生與獎學金",
        "category": "announcement"
      },
      {
        "key": "1040-679",
        "name": "研討會及相關活動",
        "category": "announcement"
      },
      {
        "key": "1040-1760",
        "name": "課程與認證",
        "category": "announcement"
      },
      {
        "key": "1040-1761",
        "name": "實習與見習",
        "category": "announcement"
      },
      {
        "key": "1040-1762",
        "name": "就業資訊",
        "category": "regulation"
      },
      {
        "key": "1040-2274",
        "name": "其他訊息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1024,
    "host": "www.ce.ntust.edu.tw",
    "unit": "工程學院、工程學士班",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1024-5",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1024-199",
        "name": "活動資訊",
        "category": "regulation"
      },
      {
        "key": "1024-1037",
        "name": "公告資訊",
        "category": "regulation"
      },
      {
        "key": "1024-2281",
        "name": "企業徵才",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1020,
    "host": "www.gsac.ntust.edu.tw",
    "unit": "自動化及控制研究所",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1020-11",
        "name": "公佈欄",
        "category": "announcement"
      },
      {
        "key": "1020-15",
        "name": "表件_其他辦法及申請書",
        "category": "regulation"
      },
      {
        "key": "1020-18",
        "name": "表件_碩士班",
        "category": "regulation"
      },
      {
        "key": "1020-409",
        "name": "表件_獎助金",
        "category": "regulation"
      },
      {
        "key": "1020-749",
        "name": "表件_博士班",
        "category": "regulation"
      },
      {
        "key": "1020-762",
        "name": "表件_修業規定",
        "category": "regulation"
      },
      {
        "key": "1020-2201",
        "name": "企業徵才",
        "category": "announcement"
      },
      {
        "key": "1020-2320",
        "name": "獎助學金",
        "category": "announcement"
      },
      {
        "key": "1020-2321",
        "name": "榮譽榜",
        "category": "news"
      }
    ]
  },
  {
    "id": 1005,
    "host": "www.me.ntust.edu.tw",
    "unit": "機械工程系",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1005-278",
        "name": "佈告欄",
        "category": "announcement"
      },
      {
        "key": "1005-279",
        "name": "課程及演講",
        "category": "announcement"
      },
      {
        "key": "1005-280",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1005-289",
        "name": "企業求才及活動",
        "category": "announcement"
      },
      {
        "key": "1005-346",
        "name": "校外實習",
        "category": "announcement"
      },
      {
        "key": "1005-858",
        "name": "競賽消息",
        "category": "announcement"
      },
      {
        "key": "1005-1363",
        "name": "獎學金",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1019,
    "host": "mse.ntust.edu.tw",
    "unit": "材料科學與工程系",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1019-6",
        "name": "課程與演講",
        "category": "announcement"
      },
      {
        "key": "1019-10",
        "name": "系辦公告",
        "category": "announcement"
      },
      {
        "key": "1019-17",
        "name": "企業徵才",
        "category": "announcement"
      },
      {
        "key": "1019-615",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1019-946",
        "name": "活動訊息",
        "category": "announcement"
      },
      {
        "key": "1019-1810",
        "name": "獎助學金",
        "category": "announcement"
      },
      {
        "key": "1019-1888",
        "name": "材料要聞",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1039,
    "host": "emrd.ntust.edu.tw",
    "unit": "高階科技研發碩士學位學程(EMRD在職專班)",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1039-1293",
        "name": "公告欄",
        "category": "announcement"
      },
      {
        "key": "1039-1366",
        "name": "活動集錦",
        "category": "news"
      },
      {
        "key": "1039-1367",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1039-1368",
        "name": "媒體報導",
        "category": "news"
      },
      {
        "key": "1039-1782",
        "name": "招生資訊",
        "category": "regulation"
      }
    ]
  },
  {
    "id": 1041,
    "host": "iatp.ntust.edu.tw",
    "unit": "先進科技全英語學士學位學程",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1041-1149",
        "name": "News",
        "category": "announcement"
      },
      {
        "key": "1041-1150",
        "name": "Events",
        "category": "announcement"
      },
      {
        "key": "1041-2016",
        "name": "Activities",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1022,
    "host": "gdep.ntust.edu.tw",
    "unit": "全球發展工程學士學位學程",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1022-1109",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1022-1113",
        "name": "活動及課程訊息",
        "category": "announcement"
      },
      {
        "key": "1022-1336",
        "name": "2TOP Summer Program",
        "category": "announcement"
      },
      {
        "key": "1022-1528",
        "name": "2TOP Summer Program專區",
        "category": "announcement"
      },
      {
        "key": "1022-2336",
        "name": "榮譽榜",
        "category": "news"
      }
    ]
  },
  {
    "id": 1103,
    "host": "semi-emrd.ntust.edu.tw",
    "unit": "半導體高階經營暨研發碩士在職學位學程(SEMI-EMRD)",
    "kind": "academic",
    "college": "工程學院",
    "boards": [
      {
        "key": "1103-1927",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1103-2130",
        "name": "招生資訊",
        "category": "regulation"
      },
      {
        "key": "1103-2218",
        "name": "活動資訊",
        "category": "regulation"
      }
    ]
  },
  {
    "id": 1001,
    "host": "www.ceecs.ntust.edu.tw",
    "unit": "電資學院、電資學士班",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1001-1",
        "name": "一般公告",
        "category": "announcement"
      },
      {
        "key": "1001-2",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1001-3",
        "name": "徵才快訊",
        "category": "announcement"
      },
      {
        "key": "1001-397",
        "name": "活動訊息",
        "category": "announcement"
      },
      {
        "key": "1001-1977",
        "name": "EMI公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1017,
    "host": "ece.ntust.edu.tw",
    "unit": "電子工程系",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1017-1",
        "name": "佈告欄",
        "category": "announcement"
      },
      {
        "key": "1017-3",
        "name": "系所資訊",
        "category": "regulation"
      },
      {
        "key": "1017-6",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1017-631",
        "name": "徵才公告",
        "category": "announcement"
      },
      {
        "key": "1017-2323",
        "name": "獎學金",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1027,
    "host": "www.ee.ntust.edu.tw",
    "unit": "電機工程系",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1027-490",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1027-1371",
        "name": "徵才公告",
        "category": "announcement"
      },
      {
        "key": "1027-1372",
        "name": "演講公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1038,
    "host": "www.csie.ntust.edu.tw",
    "unit": "資訊工程系",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1038-191",
        "name": "行政公告",
        "category": "announcement"
      },
      {
        "key": "1038-469",
        "name": "榮譽榜",
        "category": "news"
      }
    ]
  },
  {
    "id": 1018,
    "host": "www.eoe.ntust.edu.tw",
    "unit": "光電工程研究所",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1018-1",
        "name": "系所資訊",
        "category": "regulation"
      },
      {
        "key": "1018-2",
        "name": "佈告欄",
        "category": "announcement"
      },
      {
        "key": "1018-403",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1018-2322",
        "name": "獎學金",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1123,
    "host": "iict.ntust.edu.tw",
    "unit": "資通科技國際學士學位學程",
    "kind": "academic",
    "college": "電資學院",
    "boards": [
      {
        "key": "1123-1927",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1123-2310",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1123-2311",
        "name": "EMI公告",
        "category": "announcement"
      },
      {
        "key": "1123-2314",
        "name": "國際研修公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1031,
    "host": "www.management.ntust.edu.tw",
    "unit": "管理學院",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1031-7",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1031-8",
        "name": "得獎榮譽",
        "category": "news"
      },
      {
        "key": "1031-9",
        "name": "活動花絮",
        "category": "news"
      },
      {
        "key": "1031-961",
        "name": "招生訊息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1015,
    "host": "gm.ntust.edu.tw",
    "unit": "管理研究所",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1015-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1015-964",
        "name": "博士班招生資訊",
        "category": "regulation"
      },
      {
        "key": "1015-2003",
        "name": "EMBA招生資訊",
        "category": "regulation"
      },
      {
        "key": "1015-2295",
        "name": "管理學院電子報",
        "category": "announcement"
      },
      {
        "key": "1015-2296",
        "name": "管研行事曆",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1014,
    "host": "www.im.ntust.edu.tw",
    "unit": "工業管理系",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1014-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1014-5",
        "name": "就業",
        "category": "announcement"
      },
      {
        "key": "1014-902",
        "name": "實習",
        "category": "announcement"
      },
      {
        "key": "1014-903",
        "name": "演講公告",
        "category": "announcement"
      },
      {
        "key": "1014-905",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1014-2174",
        "name": "活動集錦",
        "category": "news"
      }
    ]
  },
  {
    "id": 1098,
    "host": "ba.ntust.edu.tw",
    "unit": "企業管理系",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1098-1927",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1098-1950",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1098-1951",
        "name": "活動資訊",
        "category": "regulation"
      }
    ]
  },
  {
    "id": 1002,
    "host": "www.fn.ntust.edu.tw",
    "unit": "財務金融研究所",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1002-1259",
        "name": "一般公告",
        "category": "announcement"
      },
      {
        "key": "1002-1260",
        "name": "學術活動",
        "category": "announcement"
      },
      {
        "key": "1002-1261",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1002-1262",
        "name": "實習",
        "category": "announcement"
      },
      {
        "key": "1002-2440",
        "name": "USR計畫",
        "category": "announcement"
      },
      {
        "key": "1002-2448",
        "name": "就業",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1013,
    "host": "mba.ntust.edu.tw",
    "unit": "管理學院MBA",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1013-1",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1013-955",
        "name": "活動花絮",
        "category": "news"
      },
      {
        "key": "1013-959",
        "name": "得獎榮譽",
        "category": "news"
      },
      {
        "key": "1013-1326",
        "name": "課程學分規劃",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1016,
    "host": "emba.ntust.edu.tw",
    "unit": "EMBA碩士在職專班",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1016-2",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1016-958",
        "name": "得獎榮譽",
        "category": "news"
      },
      {
        "key": "1016-963",
        "name": "招生訊息",
        "category": "announcement"
      },
      {
        "key": "1016-966",
        "name": "活動花絮",
        "category": "news"
      }
    ]
  },
  {
    "id": 1012,
    "host": "www.tm.ntust.edu.tw",
    "unit": "科技管理研究所",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1012-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1012-520",
        "name": "活動花絮",
        "category": "news"
      },
      {
        "key": "1012-1374",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1012-1840",
        "name": "研討會",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1023,
    "host": "www.mup.ntust.edu.tw",
    "unit": "管理學士班",
    "kind": "academic",
    "college": "管理學院",
    "boards": [
      {
        "key": "1023-1100",
        "name": "最新公告",
        "category": "announcement"
      },
      {
        "key": "1023-1335",
        "name": "招生訊息",
        "category": "announcement"
      },
      {
        "key": "1023-1384",
        "name": "活動花絮",
        "category": "news"
      },
      {
        "key": "1023-1385",
        "name": "得獎榮譽",
        "category": "news"
      },
      {
        "key": "1023-1856",
        "name": "實習資訊",
        "category": "regulation"
      }
    ]
  },
  {
    "id": 1028,
    "host": "dcollege.ntust.edu.tw",
    "unit": "設計學院",
    "kind": "academic",
    "college": "設計學院",
    "boards": [
      {
        "key": "1028-491",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1028-500",
        "name": "近期活動",
        "category": "announcement"
      },
      {
        "key": "1028-2246",
        "name": "EMI公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1029,
    "host": "web.lass.ntust.edu.tw",
    "unit": "人文社會學院",
    "kind": "academic",
    "college": "人文社會學院",
    "boards": [
      {
        "key": "1029-475",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1029-1239",
        "name": "人文社會學院",
        "category": "announcement"
      },
      {
        "key": "1029-2027",
        "name": "活動紀錄",
        "category": "news"
      }
    ]
  },
  {
    "id": 1006,
    "host": "www.gidle.ntust.edu.tw",
    "unit": "數位學習與教育研究所",
    "kind": "academic",
    "college": "人文社會學院",
    "boards": [
      {
        "key": "1006-159",
        "name": "公告訊息",
        "category": "announcement"
      },
      {
        "key": "1006-420",
        "name": "研討會",
        "category": "announcement"
      },
      {
        "key": "1006-422",
        "name": "口試訊息",
        "category": "announcement"
      },
      {
        "key": "1006-496",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1006-542",
        "name": "徵才與實習",
        "category": "announcement"
      },
      {
        "key": "1006-1710",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1121,
    "host": "afl.ntust.edu.tw",
    "unit": "應用外語系",
    "kind": "academic",
    "college": "人文社會學院",
    "boards": [
      {
        "key": "1121-1927",
        "name": "最新消息",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1026,
    "host": "www.doh.ntust.edu.tw",
    "unit": "跨域創新暨國際華語中心",
    "kind": "academic",
    "college": "人文社會學院",
    "boards": [
      {
        "key": "1026-503",
        "name": "最新公告",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1030,
    "host": "honor.ntust.edu.tw",
    "unit": "應用科技學院(原名：精誠榮譽學院)",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1030-2",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1030-379",
        "name": "榮譽榜",
        "category": "news"
      }
    ]
  },
  {
    "id": 1010,
    "host": "www.gsas.ntust.edu.tw",
    "unit": "應用科技研究所",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1010-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1010-2",
        "name": "公告欄",
        "category": "announcement"
      },
      {
        "key": "1010-2177",
        "name": "2024 ICMCMT 暨2024年台灣薄膜學會與台灣幾丁質幾丁聚醣學會",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1009,
    "host": "www.be.ntust.edu.tw",
    "unit": "醫學工程研究所",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1009-1",
        "name": "所辦公告",
        "category": "announcement"
      },
      {
        "key": "1009-2107",
        "name": "醫工學程資訊",
        "category": "regulation"
      },
      {
        "key": "1009-2109",
        "name": "得獎及新聞公告",
        "category": "news"
      },
      {
        "key": "1009-2258",
        "name": "招生宣傳",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1007,
    "host": "patent.ntust.edu.tw",
    "unit": "專利研究所、智慧財產權學士學位學程",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1007-1",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1007-1992",
        "name": "招生宣傳",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1011,
    "host": "color.ntust.edu.tw",
    "unit": "色彩與照明科技研究所、色彩影像與照明科技學士學位學程",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1011-1",
        "name": "徵才公告",
        "category": "announcement"
      },
      {
        "key": "1011-324",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1011-1887",
        "name": "榮譽榜",
        "category": "news"
      }
    ]
  },
  {
    "id": 1008,
    "host": "jc.ntust.edu.tw",
    "unit": "不分系學士班",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1008-2",
        "name": "最新消息",
        "category": "announcement"
      },
      {
        "key": "1008-376",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1008-378",
        "name": "學習專區",
        "category": "announcement"
      }
    ]
  },
  {
    "id": 1032,
    "host": "www.ast.ntust.edu.tw",
    "unit": "應用科技學士學位學程",
    "kind": "academic",
    "college": "應用科技學院",
    "boards": [
      {
        "key": "1032-547",
        "name": "公告訊息",
        "category": "announcement"
      },
      {
        "key": "1032-623",
        "name": "榮譽榜",
        "category": "news"
      },
      {
        "key": "1032-1803",
        "name": "課程花絮",
        "category": "news"
      }
    ]
  },
  {
    "id": 1111,
    "host": "innc.ntust.edu.tw",
    "unit": "產學創新學院、先進半導體科技研究所",
    "kind": "academic",
    "college": "產學創新學院",
    "boards": [
      {
        "key": "1111-1927",
        "name": "轉發活動訊息",
        "category": "announcement"
      },
      {
        "key": "1111-2121",
        "name": "焦點消息",
        "category": "announcement"
      },
      {
        "key": "1111-2122",
        "name": "學院公告",
        "category": "announcement"
      },
      {
        "key": "1111-2123",
        "name": "智慧製造所公告",
        "category": "announcement"
      },
      {
        "key": "1111-2124",
        "name": "人工智慧所公告",
        "category": "announcement"
      },
      {
        "key": "1111-2125",
        "name": "能源永續所公告",
        "category": "announcement"
      },
      {
        "key": "1111-2127",
        "name": "資訊公開專區",
        "category": "announcement"
      },
      {
        "key": "1111-2128",
        "name": "各系所",
        "category": "announcement"
      },
      {
        "key": "1111-2239",
        "name": "先進半導體所公告",
        "category": "announcement"
      }
    ]
  }
] satisfies Site[];

export const tags = [
  {
    "id": "topic",
    "several": true,
    "tags": [
      {
        "id": "scholarships",
        "label": "獎助學金"
      },
      {
        "id": "competitions-and-calls",
        "label": "競賽徵件"
      },
      {
        "id": "talks-and-events",
        "label": "講座活動"
      },
      {
        "id": "courses",
        "label": "課程選課"
      },
      {
        "id": "enrolment-and-grades",
        "label": "學籍成績"
      },
      {
        "id": "exams-and-certification",
        "label": "考試檢定"
      },
      {
        "id": "fees",
        "label": "繳費"
      },
      {
        "id": "housing",
        "label": "住宿"
      },
      {
        "id": "internships-and-jobs",
        "label": "實習就業"
      },
      {
        "id": "international-exchange",
        "label": "國際交流"
      },
      {
        "id": "research-projects",
        "label": "研究計畫"
      },
      {
        "id": "admissions",
        "label": "招生"
      },
      {
        "id": "venue-and-service-changes",
        "label": "場地與服務異動"
      },
      {
        "id": "safety-and-health",
        "label": "安全健康"
      },
      {
        "id": "it-systems",
        "label": "資訊系統"
      },
      {
        "id": "library",
        "label": "圖書館"
      },
      {
        "id": "military-service",
        "label": "兵役"
      },
      {
        "id": "clubs-and-volunteering",
        "label": "社團志工"
      },
      {
        "id": "rules-and-policy",
        "label": "法規制度"
      },
      {
        "id": "honours",
        "label": "榮譽賀訊"
      },
      {
        "id": "free-food",
        "label": "免費餐點"
      }
    ]
  },
  {
    "id": "audience",
    "several": true,
    "tags": [
      {
        "id": "all-students",
        "label": "全體學生"
      },
      {
        "id": "undergraduates",
        "label": "大學部"
      },
      {
        "id": "graduate-students",
        "label": "研究生"
      },
      {
        "id": "new-students",
        "label": "新生"
      },
      {
        "id": "graduating-students",
        "label": "畢業生"
      },
      {
        "id": "international-students",
        "label": "國際生"
      },
      {
        "id": "staff",
        "label": "教職員"
      },
      {
        "id": "public",
        "label": "校外"
      }
    ]
  },
  {
    "id": "nature",
    "several": false,
    "tags": [
      {
        "id": "action-required",
        "label": "需要行動"
      },
      {
        "id": "lists-and-results",
        "label": "名單結果"
      },
      {
        "id": "information",
        "label": "資訊宣導"
      },
      {
        "id": "news-and-records",
        "label": "新聞紀錄"
      }
    ]
  },
  {
    "id": "source",
    "several": false,
    "tags": [
      {
        "id": "on-campus",
        "label": "校內"
      },
      {
        "id": "forwarded",
        "label": "轉知校外"
      }
    ]
  }
] satisfies Dimension[];

/** The first two pages of the default units' stream. */
export const stream = {
  "first": {
    "items": [
      {
        "id": 1,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153593.php",
        "link_item": false,
        "title": "【招生訊息】臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
        "publisher": "專利研究所",
        "day": "2026-11-15",
        "listed_on": "2026-11-15",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1007-1",
          "1007-1992"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "admissions",
            "free-food"
          ],
          "audience": [
            "all-students",
            "staff",
            "public"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
          "summary": "臺科大專利所116學年度碩士在職專班招生說明會於11/22舉行，網路報名11/27起至12/10止。",
          "deadline": "2026-12-10"
        }
      },
      {
        "id": 2,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153597.php",
        "link_item": false,
        "title": "【學務處生輔組】115學年度第二學期本國籍升碩二學生(春季班-115年2月份入學)申請學生宿舍住宿登記辦法",
        "publisher": "學務處生輔組",
        "day": "2026-11-14",
        "listed_on": "2026-11-14",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "housing"
          ],
          "audience": [
            "graduate-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "115學年度第二學期本國籍升碩二學生(春季班-115年2月份入學)申請學生宿舍住宿登記辦法",
          "summary": "115學年度第2學期本國籍升碩二春季班學生宿舍住宿登記辦法已公告，請至學務處網頁查閱。",
          "deadline": null
        }
      },
      {
        "id": 236,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153672.php",
        "link_item": false,
        "title": "【語言中心重要通知】外語學習坊11/13上午9:10-10:00停止對外開放",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:14.627437+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "venue-and-service-changes"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "外語學習坊11/13上午9:10-10:00停止對外開放",
          "summary": "外語學習坊於11月13日上午9:10至10:00暫停對外開放。",
          "deadline": null
        }
      },
      {
        "id": 235,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153677.php",
        "link_item": false,
        "title": "【集點活動】語言中心第二場電影之夜「高年級實習生The Intern」已開放報名囉~",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:14.627437+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "語言中心第二場電影之夜「高年級實習生The Intern」已開放報名囉~",
          "summary": "語言中心11月27日舉辦電影之夜「高年級實習生」，開放線上報名，前40名提供餐點。",
          "deadline": null
        }
      },
      {
        "id": 153,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153681.php",
        "link_item": false,
        "title": "【學生活動組】2027總統教育獎遴選活動",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "2027總統教育獎遴選活動",
          "summary": "「2027總統教育獎」開放推薦，有意受推薦的同學請於115年12月10日前洽學生活動組。",
          "deadline": "2026-12-10"
        }
      },
      {
        "id": 152,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153682.php",
        "link_item": false,
        "title": "【學生活動組】轉知基隆市文化觀光局「2027基隆潮藝術藝術孵育計畫」徵件",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "轉知基隆市文化觀光局「2027基隆潮藝術藝術孵育計畫」徵件",
          "summary": "基隆市文化觀光局「2027基隆潮藝術藝術孵育計畫」徵件至115年11月30日止，每案最高補助30萬元，歡迎提案。",
          "deadline": "2026-11-30"
        }
      },
      {
        "id": 151,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153685.php",
        "link_item": false,
        "title": "【處本部】1-2、2-2「築夢」讀書計畫分享會 11/19場",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435"
        ],
        "tags": {
          "topic": [
            "scholarships",
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "1-2、2-2「築夢」讀書計畫分享會 11/19場",
          "summary": "符合築夢踏實助學金資格者可於11/17前報名11/19讀書計畫分享會。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 150,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153694.php",
        "link_item": false,
        "title": "【學生活動組】轉知「2027年SITCON學生計算機年會」開放學生議程投稿",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls",
            "talks-and-events"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "轉知「2027年SITCON學生計算機年會」開放學生議程投稿",
          "summary": "2027年SITCON學生計算機年會開放議程投稿，早鳥至11月29日止，一般投稿至2027年1月15日止。",
          "deadline": "2026-11-29"
        }
      },
      {
        "id": 149,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153698.php",
        "link_item": false,
        "title": "【生活輔導組】不利處境學生多元生理用品專項補助",
        "publisher": null,
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1437",
          "1053-1439"
        ],
        "tags": {
          "topic": [
            "scholarships"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "不利處境學生多元生理用品專項補助",
          "summary": "符合資格的生理女學生每學期可獲1,200元多元生理用品補助，第1至3類免申請，請至學籍管理系統維護郵局帳戶。",
          "deadline": null
        }
      },
      {
        "id": 12,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153675.php",
        "link_item": false,
        "title": "【周知】有關技術士技能檢定「視覺傳達設計」職類乙級（MAC細項）評估暫停辦理案",
        "publisher": "教務處註冊組",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "exams-and-certification"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "有關技術士技能檢定「視覺傳達設計」職類乙級（MAC細項）評估暫停辦理案",
          "summary": "勞動部評估暫停技術士技能檢定「視覺傳達設計」職類乙級（MAC細項），請各單位於11月19日前提供意見。",
          "deadline": "2026-11-19"
        }
      },
      {
        "id": 11,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153676.php",
        "link_item": false,
        "title": "【Forwarded Message】教學實踐南區基地謹訂於115年11月20日（五）辦理115年度教學實踐研究計畫南區基地「跨校教師社群成果交流會暨共識會議」，歡迎教師參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "教學實踐南區基地謹訂於115年11月20日（五）辦理115年度教學實踐研究計畫南區基地「跨校教師社群成果交流會暨共識會議」，歡迎教師參加。",
          "summary": "國立中山大學11月20日線上舉辦跨校教師社群成果交流會暨共識會議，請於11月18日前報名。",
          "deadline": "2026-11-18"
        }
      },
      {
        "id": 10,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153453.php",
        "link_item": false,
        "title": "【NSTC計畫徵求】國科會徵件一覽表 Forwarded Message",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [],
          "audience": [],
          "nature": [],
          "source": []
        },
        "rendition": null
      },
      {
        "id": 9,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153688.php",
        "link_item": false,
        "title": "【課程公告】國立陽明交通大學─「115年研究參與者保護倫理講習會XI」-線上課程（115/12/10）",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1055-19"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "research-projects"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立陽明交通大學─「115年研究參與者保護倫理講習會XI」-線上課程（115/12/10）",
          "summary": "陽明交大12/10舉辦研究倫理線上講習會，校外人員300元，12/1前報名。",
          "deadline": "2026-12-01"
        }
      },
      {
        "id": 8,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153695.php",
        "link_item": false,
        "title": "【Forwarded Message】教學實踐研究計畫中部區域基地謹訂於115年12月1日辦理「教學實踐研究計畫撰稿工作坊」，歡迎教師參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "research-projects"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "教學實踐研究計畫中部區域基地謹訂於115年12月1日辦理「教學實踐研究計畫撰稿工作坊」，歡迎教師參加。",
          "summary": "教學實踐研究計畫撰稿工作坊12月1日於靜宜大學舉行，教師可於11月26日13:00前報名。",
          "deadline": "2026-11-26"
        }
      },
      {
        "id": 7,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153697.php",
        "link_item": false,
        "title": "【Forwarded Message】國立暨南國際大學辦理「敘事教學作為校園抵抗性別歧視的行動：我的同志生命美學」教師教學知能活動，歡迎教師參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立暨南國際大學辦理「敘事教學作為校園抵抗性別歧視的行動：我的同志生命美學」教師教學知能活動，歡迎教師參加。",
          "summary": "國立暨南國際大學11月18日舉辦線上教師教學知能活動，請於11月17日13:00前線上報名。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 6,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153699.php",
        "link_item": false,
        "title": "【Forwarded Message】國立臺中教育大學教務處教學發展組辦理115學年度第1學期教師知能生成式AI系列專題講座，歡迎教職員生參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立臺中教育大學教務處教學發展組辦理115學年度第1學期教師知能生成式AI系列專題講座，歡迎教職員生參加。",
          "summary": "國立臺中教育大學於12月8日舉辦生成式AI專題線上講座，即日起至12月4日開放全國大專院校教職員生報名。",
          "deadline": "2026-12-04"
        }
      },
      {
        "id": 5,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153696.php",
        "link_item": false,
        "title": "【學生活動組】校外活動訊息轉知",
        "publisher": "學務處學生活動組",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls",
            "talks-and-events"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "校外活動訊息轉知",
          "summary": "學務處轉知2027總統教育獎遴選、基隆潮藝術徵件及SITCON學生計算機年會投稿等校外活動及競賽訊息。",
          "deadline": null
        }
      },
      {
        "id": 4,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153701.php",
        "link_item": false,
        "title": "【NSTC計畫徵求】「2027年臺德(NSTC-DAAD)青年暑期營計畫」，請於2026年1月18日(一)下午5時前完成線上申請，逾期不予受理，請查照。",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1055-19"
        ],
        "tags": {
          "topic": [
            "international-exchange",
            "research-projects"
          ],
          "audience": [
            "graduate-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "「2027年臺德(NSTC-DAAD)青年暑期營計畫」，請於2026年1月18日(一)下午5時前完成線上申請，逾期不予受理，請查照。",
          "summary": "2027年臺德青年暑期營計畫受理申請，非人文社會領域碩博士生請於2026年1月18日下午5時前完成線上申請。",
          "deadline": "2026-01-18"
        }
      },
      {
        "id": 3,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-151791.php",
        "link_item": false,
        "title": "成果展 × 烤布蕾 × 皮克敏！2026 社會實踐博覽會搶先看(115.12.10)",
        "publisher": "通識教育中心",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "成果展 × 烤布蕾 × 皮克敏！2026 社會實踐博覽會搶先看(115.12.10)",
          "summary": "12月10日第四教學大樓川堂舉辦社會實踐博覽會，現場有成果展、集點兌換及抽獎活動。",
          "deadline": null
        }
      },
      {
        "id": 223,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153668.php",
        "link_item": false,
        "title": "【活動公告】115-1 第二場11/25哈拉文化活動:Dating Etiquette報名成功清單",
        "publisher": null,
        "day": "2026-11-12",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:12.476048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1050",
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "undergraduates"
          ],
          "nature": [
            "lists-and-results"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "115-1 第二場11/25哈拉文化活動:Dating Etiquette報名成功清單",
          "summary": "11/25 12:20於IB-202舉辦哈拉文化活動，請錄取者準時入場並依需求攜帶認證表單。",
          "deadline": null
        }
      },
      {
        "id": 156,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153660.php",
        "link_item": false,
        "title": "【處本部】1-2、2-2「築夢」讀書計畫分享會 11/18場",
        "publisher": null,
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435"
        ],
        "tags": {
          "topic": [
            "scholarships",
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "1-2、2-2「築夢」讀書計畫分享會 11/18場",
          "summary": "符合築夢踏實助學金資格的在學學生，請於 11 月 16 日中午 12 時前報名參加 11 月 18 日讀書計畫分享會。",
          "deadline": "2026-11-16"
        }
      },
      {
        "id": 155,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153666.php",
        "link_item": false,
        "title": "【學生活動組】中華民國紅十字會招募第4屆寒假「青年防災士服務隊」（報名至115年12月11日止）",
        "publisher": null,
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "clubs-and-volunteering"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "中華民國紅十字會招募第4屆寒假「青年防災士服務隊」（報名至115年12月11日止）",
          "summary": "紅十字會招募寒假青年防災士服務隊，12月11日報名截止，全程免費並可取得雙證照與5,000元獎助金。",
          "deadline": "2026-12-11"
        }
      },
      {
        "id": 154,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153667.php",
        "link_item": false,
        "title": "【學生活動組】轉知國立臺灣師範大學「2027年第59屆國際化學奧林匹亞競賽（IChO 2027）」隨隊志工招募",
        "publisher": null,
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "international-exchange",
            "clubs-and-volunteering"
          ],
          "audience": [
            "undergraduates",
            "graduate-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "轉知國立臺灣師範大學「2027年第59屆國際化學奧林匹亞競賽（IChO 2027）」隨隊志工招募",
          "summary": "2027 IChO 隨隊志工招募，歡迎具備英語B2以上之大專生及碩士生於2027年1月29日前線上報名。",
          "deadline": "2027-01-29"
        }
      },
      {
        "id": 33,
        "site": 1049,
        "unit": "圖書館",
        "url": "https://library.ntust.edu.tw/p/406-1049-153636.php",
        "link_item": false,
        "title": "【三校聯盟】新文藝復興 X 115年臺師大圖書館閱讀節活動宣傳",
        "publisher": null,
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:55.676659+00:00",
        "withdrawn_at": null,
        "boards": [
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "新文藝復興 X 115年臺師大圖書館閱讀節活動宣傳",
          "summary": "臺師大圖書館於11月17日起舉辦「新文藝復興」閱讀節，包含特展、開幕式與專題演講，歡迎報名參加。",
          "deadline": null
        }
      },
      {
        "id": 18,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153624.php",
        "link_item": false,
        "title": "【轉知】2026日本語道場活動",
        "publisher": "語言中心",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "2026日本語道場活動",
          "summary": "陽明交大於11月21日舉辦2026日本語道場，歡迎具備N3以上日文能力之大專校院學生報名。",
          "deadline": null
        }
      },
      {
        "id": 17,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153629.php",
        "link_item": false,
        "title": "【轉知】國家科學及技術委員會「創新創業激勵計畫」2027第一梯次培訓公開徵件，截至2026年12月30日中午12:00止",
        "publisher": "產學營運處育成中心",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國家科學及技術委員會「創新創業激勵計畫」2027第一梯次培訓公開徵件，截至2026年12月30日中午12:00止",
          "summary": "國科會「創新創業激勵計畫」2027第一梯次徵件至2026年12月30日中午12:00止，歡迎有意創業的師生報名。",
          "deadline": "2026-12-30"
        }
      },
      {
        "id": 16,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153626.php",
        "link_item": false,
        "title": "慶祝圖書館大樓50歲~ 敬邀您參與解開時光密碼，抽禮券！還能在留言牆寫下給圖書館的祝福！",
        "publisher": "圖書館",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "慶祝圖書館大樓50歲~ 敬邀您參與解開時光密碼，抽禮券！還能在留言牆寫下給圖書館的祝福！",
          "summary": "圖書館50週年活動自11/11至11/25止，本校教職員工生可參加「時空檔案」線上解謎抽禮券，或至一樓留言牆寫下祝福。",
          "deadline": "2026-11-25"
        }
      },
      {
        "id": 15,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153646.php",
        "link_item": false,
        "title": "【請留意送審時程】臺大行為與社會科學研究倫理中心送審規範與證明核發時程提醒（NTU Behavioral and Social Sciences Research Ethics Committee (REC) Review Guidelines & Submission Proof Processing Timeline）",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1055-19"
        ],
        "tags": {
          "topic": [
            "research-projects"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "臺大行為與社會科學研究倫理中心送審規範與證明核發時程提醒（NTU Behavioral and Social Sciences Research Ethics Committee (REC) Review Guidelines & Submission Proof Processing Timeline）",
          "summary": "國科會116年度專題研究計畫12月31日中午截止，請留意臺大倫審中心送審時程並提早送件。",
          "deadline": "2026-12-31"
        }
      },
      {
        "id": 14,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153650.php",
        "link_item": false,
        "title": "【Forwarded Message】國立高雄大學 創新學院辦理「AI工具融入教學與研究」系列教師增能研習資訊，敬請惠予公告並協助宣傳，歡迎教職員生參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立高雄大學 創新學院辦理「AI工具融入教學與研究」系列教師增能研習資訊，敬請惠予公告並協助宣傳，歡迎教職員生參加。",
          "summary": "國立高雄大學辦理「AI工具融入教學與研究」線上研習，歡迎教職員生報名參加。",
          "deadline": null
        }
      },
      {
        "id": 13,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153651.php",
        "link_item": false,
        "title": "【轉知】國立高雄師範大學工業科技教育學系辦理之「2027第23屆科技教育研究與發展學術研討會」論文徵稿資訊，請踴躍參加。",
        "publisher": "秘書室",
        "day": "2026-11-12",
        "listed_on": "2026-11-12",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls",
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立高雄師範大學工業科技教育學系辦理之「2027第23屆科技教育研究與發展學術研討會」論文徵稿資訊，請踴躍參加。",
          "summary": "國立高雄師範大學辦理「2027第23屆科技教育研究與發展學術研討會」，歡迎相關系所師生踴躍投稿及報名參加。",
          "deadline": null
        }
      }
    ],
    "next": "MjAyNi0xMS0xMi4xMw"
  },
  "second": {
    "items": [
      {
        "id": 1697,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153594.php",
        "link_item": false,
        "title": "【生活輔導組】國立臺灣科技大學 115學年度第二學期本國籍升碩二學生(春季班)申請學生宿舍住宿登記辦法",
        "publisher": null,
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:23:56.679824+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1436"
        ],
        "tags": {
          "topic": [
            "housing"
          ],
          "audience": [
            "graduate-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "國立臺灣科技大學 115學年度第二學期本國籍升碩二學生(春季班)申請學生宿舍住宿登記辦法",
          "summary": "115-2本國籍春季班升碩二生欲申請宿舍者，請於11月16日至25日中午12時前完成線上登記，並依限繳交戶籍資料。",
          "deadline": "2026-11-25"
        }
      },
      {
        "id": 209,
        "site": 1060,
        "unit": "國際事務處",
        "url": "https://www.oia.ntust.edu.tw/p/406-1060-153595.php",
        "link_item": false,
        "title": "【轉知】奧地利姐妹校TU Graz將於11月24日舉辦線上說明會，歡迎同學參加！",
        "publisher": null,
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:13:07.484048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1060-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "international-exchange"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "奧地利姐妹校TU Graz將於11月24日舉辦線上說明會，歡迎同學參加！",
          "summary": "奧地利姐妹校TU Graz將於11月24日舉辦線上交換說明會，請於11月23日12:00（CET）前線上報名。",
          "deadline": "2026-11-23"
        }
      },
      {
        "id": 34,
        "site": 1049,
        "unit": "圖書館",
        "url": "https://library.ntust.edu.tw/p/406-1049-153071.php",
        "link_item": false,
        "title": "🔔叮咚! 好書快遞到囉！完成跨校區圖書調閱，好禮等你帶回家！",
        "publisher": null,
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:55.676659+00:00",
        "withdrawn_at": null,
        "boards": [
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "library"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "叮咚! 好書快遞到囉！完成跨校區圖書調閱，好禮等你帶回家！",
          "summary": "11/16前使用跨校區圖書調閱並借閱至少一天，即可參加抽獎。",
          "deadline": "2026-11-16"
        }
      },
      {
        "id": 25,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153596.php",
        "link_item": false,
        "title": "【轉知】「國立高雄科技大學海外頂尖大學申請指南講座」及「2027 高科大 WINNING 新加坡頂尖大學短期參訪團」",
        "publisher": "國際事務處",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "international-exchange"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "「國立高雄科技大學海外頂尖大學申請指南講座」及「2027 高科大 WINNING 新加坡頂尖大學短期參訪團」",
          "summary": "高科大舉辦新加坡頂尖大學申請指南講座（11/21）及2027年1月短期參訪團，歡迎學生報名參加。",
          "deadline": null
        }
      },
      {
        "id": 24,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153598.php",
        "link_item": false,
        "title": "【轉知】奧地利姐妹校TU Graz將於11月24日舉辦線上說明會，歡迎同學參加！Online Info Session about Graz University of Technology (TU Graz), Austria",
        "publisher": "國際事務處",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "international-exchange"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "奧地利姐妹校TU Graz將於11月24日舉辦線上說明會，歡迎同學參加！Online Info Session about Graz University of Technology (TU Graz), Austria",
          "summary": "奧地利姐妹校 TU Graz 將於 11/24 舉辦線上交換說明會，請於 11/23 12:00 (CET) 前報名。",
          "deadline": "2026-11-23"
        }
      },
      {
        "id": 23,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153600.php",
        "link_item": false,
        "title": "【轉知】溫世仁文教基金會-2026 NXT Fresh 人才培育計畫 - 春季班即將開放報名，詳見官網!",
        "publisher": "國際事務處",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1060-1"
        ],
        "tags": {
          "topic": [
            "internships-and-jobs"
          ],
          "audience": [
            "undergraduates",
            "graduate-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "溫世仁文教基金會-2026 NXT Fresh 人才培育計畫 - 春季班即將開放報名，詳見官網!",
          "summary": "溫世仁文教基金會 2026 NXT Fresh 春季班即將開放報名，歡迎大三以上在學生及兩年內社會新鮮人參與。",
          "deadline": null
        }
      },
      {
        "id": 22,
        "site": 1068,
        "unit": "環安室",
        "url": "https://she.ntust.edu.tw/p/406-1068-152869.php",
        "link_item": false,
        "title": "【防疫宣導】鼠害防治及物資領用公告",
        "publisher": "環安室",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1068-1497",
          "1068-2412",
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "safety-and-health"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "鼠害防治及物資領用公告",
          "summary": "各單位可向環安室登記領用鼠害防治物資，並於領取黏鼠板後兩週內繳交使用紀錄表。",
          "deadline": null
        }
      },
      {
        "id": 21,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153607.php",
        "link_item": false,
        "title": "【NSTC獎學金】國科會115年度優博獎學金受獎名單公告",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1055-19"
        ],
        "tags": {
          "topic": [
            "scholarships"
          ],
          "audience": [
            "graduate-students"
          ],
          "nature": [
            "lists-and-results"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "國科會115年度優博獎學金受獎名單公告",
          "summary": "公告國科會115年度博士生研究獎學金受獎名單，相關事宜請洽教務處研教組王先生（分機7361）。",
          "deadline": null
        }
      },
      {
        "id": 20,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153609.php",
        "link_item": false,
        "title": "華夏校區圖書館11/16(一)至11/26(四)部分區域施工，3樓至5樓閱覽空間暫時關閉",
        "publisher": "圖書館",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "venue-and-service-changes",
            "library"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "華夏校區圖書館11/16(一)至11/26(四)部分區域施工，3樓至5樓閱覽空間暫時關閉",
          "summary": "華夏校區圖書館11/16至11/26施工，3至5樓閱覽空間暫時關閉，請改用1、2樓。",
          "deadline": null
        }
      },
      {
        "id": 19,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153552.php",
        "link_item": false,
        "title": "11/13(五)充實午休時光！從菜鳥翻身到心靈安穩：兩本改變思維的必讀好書--報名就送餐盒",
        "publisher": "圖書館",
        "day": "2026-11-11",
        "listed_on": "2026-11-11",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "11/13(五)充實午休時光！從菜鳥翻身到心靈安穩：兩本改變思維的必讀好書--報名就送餐盒",
          "summary": "11/13 圖書館「閱讀.悅讀」心得分享活動開放報名，提前報名並參與者可領取餐盒。",
          "deadline": null
        }
      },
      {
        "id": 237,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153550.php",
        "link_item": false,
        "title": "【重要公告】115學年度「校定英文能力檢測會考」符合資格名單",
        "publisher": null,
        "day": "2026-11-10",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:14.627437+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "exams-and-certification"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "lists-and-results"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "115學年度「校定英文能力檢測會考」符合資格名單",
          "summary": "115學年度校定英文能力檢測會考符合資格名單已公告，請於11月30日至12月4日完成保證金繳費與證明上傳。",
          "deadline": "2026-12-04"
        }
      },
      {
        "id": 210,
        "site": 1060,
        "unit": "國際事務處",
        "url": "https://www.oia.ntust.edu.tw/p/406-1060-153576.php",
        "link_item": false,
        "title": "11月19日(四) 德國 Esslingen University of Applied Sciences、法國 Burgundy School of Business 交換機會線上說明會，歡迎同學踴躍參加！",
        "publisher": null,
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:13:07.484048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1060-1",
          "1060-364"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "international-exchange"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "11月19日(四) 德國 Esslingen University of Applied Sciences、法國 Burgundy School of Business 交換機會線上說明會，歡迎同學踴躍參加！",
          "summary": "國際處將於11月19日舉辦德國與法國姊妹校交換線上說明會，報名至11月17日16:00止。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 157,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153587.php",
        "link_item": false,
        "title": "【學生活動組】轉知中華民國各界慶祝116年青年節表揚大專優秀青年遴選要點",
        "publisher": null,
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls",
            "honours"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "轉知中華民國各界慶祝116年青年節表揚大專優秀青年遴選要點",
          "summary": "有意參加116年大專優秀青年遴選的同學，請於116年1月31日前將同意書與優良事蹟資料送至學生活動組。",
          "deadline": "2027-01-31"
        }
      },
      {
        "id": 36,
        "site": 1049,
        "unit": "圖書館",
        "url": "https://library.ntust.edu.tw/p/406-1049-153579.php",
        "link_item": false,
        "title": "【線上講座】 Cell Press 化學領域期刊投稿線上研討會，歡迎報名參加",
        "publisher": null,
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:55.676659+00:00",
        "withdrawn_at": null,
        "boards": [
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "Cell Press 化學領域期刊投稿線上研討會，歡迎報名參加",
          "summary": "Elsevier 將於 11 月 25 日舉辦 Cell Press 化學領域期刊投稿線上研討會，歡迎師生報名。",
          "deadline": null
        }
      },
      {
        "id": 35,
        "site": 1049,
        "unit": "圖書館",
        "url": "https://library.ntust.edu.tw/p/406-1049-153580.php",
        "link_item": false,
        "title": "【線上講座】Springer「 學術期刊論文寫作與AI應用」投稿線上講座，歡迎報名參加",
        "publisher": null,
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:55.676659+00:00",
        "withdrawn_at": null,
        "boards": [
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "Springer「 學術期刊論文寫作與AI應用」投稿線上講座，歡迎報名參加",
          "summary": "Springer 將於 11 月 19 日舉辦「學術期刊論文寫作與AI應用」線上講座，歡迎報名參加。",
          "deadline": null
        }
      },
      {
        "id": 30,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153572.php",
        "link_item": false,
        "title": "【教育部計畫徵求】116年「教育部補助辦理藝術教育活動」",
        "publisher": "研發處計畫業務服務中心",
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391",
          "1055-19"
        ],
        "tags": {
          "topic": [
            "research-projects"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "116年「教育部補助辦理藝術教育活動」",
          "summary": "教育部116年藝術教育活動補助分1月及7月兩梯次線上申請，請於2月1日及8月2日下午5時前完成填報。",
          "deadline": "2027-02-01"
        }
      },
      {
        "id": 29,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153582.php",
        "link_item": false,
        "title": "【Forwarded Message】教學實踐研究計畫北區基地訂於115年11月12日、12月8日辦理「創新教學AI線上工作坊」，歡迎教師參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "教學實踐研究計畫北區基地訂於115年11月12日、12月8日辦理「創新教學AI線上工作坊」，歡迎教師參加。",
          "summary": "北區基地於11月12日及12月8日舉辦創新教學AI線上工作坊，歡迎教師線上報名。",
          "deadline": "2026-11-11"
        }
      },
      {
        "id": 28,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153583.php",
        "link_item": false,
        "title": "【Forwarded Message】國立中山大學教務處謹訂於115年11月20日(星期五)辦理教師成長工作坊「教AI、用AI、與AI共學：AI時代大學教學的重新設計與反思」，歡迎教師參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立中山大學教務處謹訂於115年11月20日(星期五)辦理教師成長工作坊「教AI、用AI、與AI共學：AI時代大學教學的重新設計與反思」，歡迎教師參加。",
          "summary": "國立中山大學11月20日辦理AI教學教師成長工作坊，請於11月17日前報名。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 27,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153585.php",
        "link_item": false,
        "title": "【Forwarded Message】國立臺灣師範大學表演藝術學系謹訂於115年12月4日（星期五）舉辦「2026表演藝術管理領導力論壇」，歡迎師生參加。",
        "publisher": "教務處教學發展中心",
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff",
            "public"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "國立臺灣師範大學表演藝術學系謹訂於115年12月4日（星期五）舉辦「2026表演藝術管理領導力論壇」，歡迎師生參加。",
          "summary": "臺師大12月4日舉辦2026表演藝術管理領導力論壇，免費參加，歡迎師生報名。",
          "deadline": null
        }
      },
      {
        "id": 26,
        "site": 1045,
        "unit": "全校公佈欄",
        "url": "https://bulletin.ntust.edu.tw/p/406-1045-153586.php",
        "link_item": false,
        "title": "11月19日(四) 德國 Esslingen University of Applied Sciences、法國 Burgundy School of Business 交換機會線上說明會 Online Exchange Opportunities Briefing Session",
        "publisher": "國際事務處",
        "day": "2026-11-10",
        "listed_on": "2026-11-10",
        "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
        "withdrawn_at": null,
        "boards": [
          "1045-1391"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "international-exchange"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "11月19日(四) 德國 Esslingen University of Applied Sciences、法國 Burgundy School of Business 交換機會線上說明會 Online Exchange Opportunities Briefing Session",
          "summary": "國際處11月19日舉辦德、法姊妹校交換機會線上說明會，請於11月17日16:00前報名。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 211,
        "site": 1060,
        "unit": "國際事務處",
        "url": "https://www.oia.ntust.edu.tw/p/406-1060-153512.php",
        "link_item": false,
        "title": "【轉知】學術交流基金會於116年1月及2月（寒假期間），舉辦「115學年度Fulbright Taiwan免試托福計畫美國學術文化暨研究所前導海外研修」活動",
        "publisher": null,
        "day": "2026-11-09",
        "listed_on": "2026-11-09",
        "first_seen_at": "2026-11-15T05:13:07.484048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1060-1"
        ],
        "tags": {
          "topic": [
            "international-exchange"
          ],
          "audience": [
            "undergraduates"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "學術交流基金會於116年1月及2月（寒假期間），舉辦「115學年度Fulbright Taiwan免試托福計畫美國學術文化暨研究所前導海外研修」活動",
          "summary": "學術交流基金會開放大一至大四生申請115學年度寒假赴美研習，11月27日截止線上報名。",
          "deadline": "2026-11-27"
        }
      },
      {
        "id": 37,
        "site": 1049,
        "unit": "圖書館",
        "url": "https://library.ntust.edu.tw/p/406-1049-153449.php",
        "link_item": false,
        "title": "【電影欣賞活動】圖書館電影欣賞《陽光女子合唱團》11月18日(三) 17:30-19:44，歡迎踴躍參與！",
        "publisher": null,
        "day": "2026-11-09",
        "listed_on": "2026-11-09",
        "first_seen_at": "2026-11-15T05:12:55.676659+00:00",
        "withdrawn_at": null,
        "boards": [
          "1049-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "圖書館電影欣賞《陽光女子合唱團》11月18日(三) 17:30-19:44，歡迎踴躍參與！",
          "summary": "圖書館將於11/18舉辦《陽光女子合唱團》電影欣賞，請於11/17中午12時前上網報名，前30名會後提供餐盒。",
          "deadline": "2026-11-17"
        }
      },
      {
        "id": 158,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153455.php",
        "link_item": false,
        "title": "【學生活動組】轉知教育部青年發展署第4屆「青年志工行動競賽表揚計畫（青志獎）」受理報名",
        "publisher": null,
        "day": "2026-11-06",
        "listed_on": "2026-11-06",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls",
            "clubs-and-volunteering"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "轉知教育部青年發展署第4屆「青年志工行動競賽表揚計畫（青志獎）」受理報名",
          "summary": "教育部青志獎即日起至12月21日中午12時止受理線上報名，歡迎15至35歲青年志工團隊及推動單位參加。",
          "deadline": "2026-12-21"
        }
      },
      {
        "id": 225,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153437.php",
        "link_item": false,
        "title": "【活動公告】115-1 第二場哈拉文化活動Dating Etiquette開放報名中",
        "publisher": null,
        "day": "2026-11-05",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:12.476048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1050",
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "115-1 第二場哈拉文化活動Dating Etiquette開放報名中",
          "summary": "115-1 第二場哈拉文化活動「Dating Etiquette」將於 11 月 25 日舉行，歡迎報名，前 40 名錄取者提供餐點。",
          "deadline": null
        }
      },
      {
        "id": 213,
        "site": 1060,
        "unit": "國際事務處",
        "url": "https://www.oia.ntust.edu.tw/p/406-1060-153399.php",
        "link_item": false,
        "title": "【轉知】芬蘭姐妹校 Aalto University Summer Research Program 2027",
        "publisher": null,
        "day": "2026-11-05",
        "listed_on": "2026-11-05",
        "first_seen_at": "2026-11-15T05:13:07.484048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1060-1"
        ],
        "tags": {
          "topic": [
            "international-exchange",
            "research-projects"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "芬蘭姐妹校 Aalto University Summer Research Program 2027",
          "summary": "芬蘭姊妹校 Aalto University 暑期研究計畫將於 2027/1/7 至 1/31 開放申請，提供每月 €2,000 起津貼。",
          "deadline": "2027-01-31"
        }
      },
      {
        "id": 212,
        "site": 1060,
        "unit": "國際事務處",
        "url": "https://www.oia.ntust.edu.tw/p/406-1060-153424.php",
        "link_item": false,
        "title": "【轉知】2026 臺大排燈節活動邀請",
        "publisher": null,
        "day": "2026-11-05",
        "listed_on": "2026-11-05",
        "first_seen_at": "2026-11-15T05:13:07.484048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1060-1"
        ],
        "tags": {
          "topic": [
            "talks-and-events"
          ],
          "audience": [
            "all-students",
            "staff",
            "public"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "2026 臺大排燈節活動邀請",
          "summary": "臺大印度學生會於 11/15 舉辦「2026 排燈節之夜」，歡迎師生及親友購票參加。",
          "deadline": null
        }
      },
      {
        "id": 160,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153420.php",
        "link_item": false,
        "title": "【學生活動組】永長興社會福利慈善基金會「2026年大專青年公益提案競賽」，歡迎同學踴躍參加",
        "publisher": null,
        "day": "2026-11-05",
        "listed_on": "2026-11-05",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435",
          "1053-1440"
        ],
        "tags": {
          "topic": [
            "competitions-and-calls"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "action-required"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "永長興社會福利慈善基金會「2026年大專青年公益提案競賽」，歡迎同學踴躍參加",
          "summary": "永長興基金會2026大專青年公益提案競賽開放報名，請於2026年12月31日前繳交訪查報告與協助計畫。",
          "deadline": "2026-12-31"
        }
      },
      {
        "id": 159,
        "site": 1053,
        "unit": "學生事務處",
        "url": "https://student.ntust.edu.tw/p/406-1053-153434.php",
        "link_item": false,
        "title": "【生活輔導組】115年度大專校院學務工作計畫「校園法治素養強化計畫」研習活動",
        "publisher": null,
        "day": "2026-11-05",
        "listed_on": "2026-11-05",
        "first_seen_at": "2026-11-15T05:13:00.636172+00:00",
        "withdrawn_at": null,
        "boards": [
          "1053-1435"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "safety-and-health"
          ],
          "audience": [
            "all-students",
            "staff"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "forwarded"
          ]
        },
        "rendition": {
          "title": "115年度大專校院學務工作計畫「校園法治素養強化計畫」研習活動",
          "summary": "教育部「校園法治素養強化計畫」研習活動於11月20日在真理大學舉行，請至線上報名。",
          "deadline": null
        }
      },
      {
        "id": 227,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153325.php",
        "link_item": false,
        "title": "【活動轉發】FSE NTUST EMI Support Team-英文寫作及口說工作坊 (場次四)",
        "publisher": null,
        "day": "2026-11-04",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:12.476048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1050",
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "FSE NTUST EMI Support Team-英文寫作及口說工作坊 (場次四)",
          "summary": "FSE EMI 團隊於 11/19 舉辦托福寫作工作坊，提供餐點與認證章，歡迎臺科大學生報名。",
          "deadline": null
        }
      },
      {
        "id": 226,
        "site": 1070,
        "unit": "語言中心",
        "url": "https://lc.ntust.edu.tw/p/406-1070-153352.php",
        "link_item": false,
        "title": "【活動緊急通知】115-1語言中心第四場英語角落活動(延後至12/1中午辦理)",
        "publisher": null,
        "day": "2026-11-04",
        "listed_on": null,
        "first_seen_at": "2026-11-15T05:13:12.476048+00:00",
        "withdrawn_at": null,
        "boards": [
          "1070-1050",
          "1070-1053"
        ],
        "tags": {
          "topic": [
            "talks-and-events",
            "free-food"
          ],
          "audience": [
            "all-students"
          ],
          "nature": [
            "information"
          ],
          "source": [
            "on-campus"
          ]
        },
        "rendition": {
          "title": "115-1語言中心第四場英語角落活動(延後至12/1中午辦理)",
          "summary": "115-1語言中心第四場英語角落活動延後至12月1日中午於IB-505辦理，報名成功者可領取餐點。",
          "deadline": null
        }
      }
    ],
    "next": "MjAyNi0xMS0wNC4yMjY"
  }
} satisfies Record<string, Page>;

export const articles = {
  "1": {
    "id": 1,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153593.php",
    "link_item": false,
    "title": "【招生訊息】臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
    "publisher": "專利研究所",
    "day": "2026-11-15",
    "listed_on": "2026-11-15",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391",
      "1007-1",
      "1007-1992"
    ],
    "tags": {
      "topic": [
        "talks-and-events",
        "admissions",
        "free-food"
      ],
      "audience": [
        "all-students",
        "staff",
        "public"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "on-campus"
      ]
    },
    "rendition": {
      "title": "臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
      "summary": "臺科大專利所116學年度碩士在職專班招生說明會於11/22舉行，網路報名11/27起至12/10止。",
      "deadline": "2026-12-10",
      "markdown": "### 招生說明會資訊\n\n- **日期：**115年11月22日（週日），開放同步遠距參加\n- **時間：**上午 10:00 - 11:00\n- **地點：**本校研揚大樓八樓（TR-829）\n- **遠距參加：**[遠距會議連結](https://meet.google.com/gcr-cxec-apf)\n- **報名方式：**[線上報名招生說明會](https://forms.gle/GPqQa5mFhB1Mf3dA6)\n- **實體參與福利：**提供西點餐盒一份\n\n打造跨域競爭優勢，結合技術、法律與管理，培養專業智慧財產人才。\n[觀看 116 學年度臺科大專利所碩士在職專班招生宣傳影片](https://youtu.be/m9DPvXdSeJc)\n\n### 碩士在職專班招生資訊\n\n- **網路報名時間：**115年11月27日（星期五）上午 9:00 起至 **115年12月10日（星期四）下午 5:00 止**\n- **招生簡章與資訊：**[臺科大 116 學年度碩士在職專班招生資訊](https://www.admission.ntust.edu.tw/p/405-1052-153258,c8737.php?Lang=zh-tw)"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\t\t\n\t\n\t\n   <div class=\"meditor\"><h1>臺科大專利所 116 學年度碩士在職專班招生說明會</h1>\n\n\n<ul>\n\t<li><strong>日期：</strong>115年11月22日（週日）開放同步遠距參加。</li>\n\t<li><strong>遠距參加網址: </strong><a href=\"https://meet.google.com/gcr-cxec-apf\" title=\"116學年度招說會遠距網址\"> <span style=\"font-size:12pt\"><span style=\"line-height:115%\"><span style=\"font-family:Aptos,sans-serif\">https://meet.google.com/gcr-cxec-apf</span></span></span></a></li>\n\t<li><strong>時間：</strong>上午 10:00 - 11:00</li>\n\t<li><strong>地點：</strong>本校研揚大樓八樓(TR-829)</li>\n\t<li><strong>報名招生說明會：</strong><a href=\"https://forms.gle/GPqQa5mFhB1Mf3dA6\" title=\"116學年度臺科大專利所碩專班招說會報名表\">https://forms.gle/GPqQa5mFhB1Mf3dA6</a></li>\n\t<li><strong>實體參與提供西點餐盒一份！</strong></li>\n</ul>\n\n\n<p> </p>\n\n\n<p>打造跨域競爭優勢 成就無可取代的你<br>\n技術 x 法律 x 管理<br>\n培養專業的智慧財產人才</p>\n\n\n<p><a href=\"https://youtu.be/m9DPvXdSeJc\" title=\"116碩專班招生宣傳影片\">觀看 116 學年度臺科大專利所碩士在職專班招生宣傳影片（YouTube，另開新視窗） </a></p>\n\n<hr>\n<h2 id=\"master-admission-title\">臺科大專利所碩士在職專班招生資訊</h2>\n\n<p><strong>網路報名時間：</strong>115年11月27日（星期五）上午 9:00 起至 115年12月10日（星期四）下午 5:00 止</p>\n\n<p><strong>本校招生資訊：</strong><a href=\"https://www.admission.ntust.edu.tw/p/405-1052-153258,c8737.php?Lang=zh-tw\" title=\"116臺科大碩專班招生資訊\"> 臺科大 116 學年度碩士在職專班招生資訊（另開新視窗）</a></p>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">專利研究所</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">muser-xx-xxxx,stud-xxxx-xd</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校本國學生, 全校教職員工</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:29:45.995951+00:00"
      }
    ],
    "cross_posts": [
      {
        "id": 794,
        "site": 1007,
        "url": "https://patent.ntust.edu.tw/p/406-1007-153457.php"
      }
    ],
    "cross_post_of": null
  },
  "4": {
    "id": 4,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153701.php",
    "link_item": false,
    "title": "【NSTC計畫徵求】「2027年臺德(NSTC-DAAD)青年暑期營計畫」，請於2026年1月18日(一)下午5時前完成線上申請，逾期不予受理，請查照。",
    "publisher": "研發處計畫業務服務中心",
    "day": "2026-11-13",
    "listed_on": "2026-11-13",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391",
      "1055-19"
    ],
    "tags": {
      "topic": [
        "international-exchange",
        "research-projects"
      ],
      "audience": [
        "graduate-students"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "forwarded"
      ]
    },
    "rendition": {
      "title": "「2027年臺德(NSTC-DAAD)青年暑期營計畫」，請於2026年1月18日(一)下午5時前完成線上申請，逾期不予受理，請查照。",
      "summary": "2027年臺德青年暑期營計畫受理申請，非人文社會領域碩博士生請於2026年1月18日下午5時前完成線上申請。",
      "deadline": "2026-01-18",
      "markdown": "依國科會與德國學術交流總署（DAAD）簽署之「青年暑期營合作備忘錄」辦理，提供年輕學子暑期赴對方大學或研究機構研習之機會。\n\n- **申請資格**：非人文社會領域科系且研習期間仍在學之碩、博士班學生，並能於 116 年暑期（7 月至 9 月）赴德國研習者。\n- **申請期限**：請於 **2026年1月18日（一）下午5時前** 完成線上申請，逾期不予受理。\n- **申請方式**：本項徵求計畫案已同步公告於國科會網站，有意申請者應依說明於線上填寫及上傳送出。詳情請參閱[申請須知](https://rd-r.ntust.edu.tw/var/file/55/1055/img/413945039.pdf)及[來文電子檔](https://rd-r.ntust.edu.tw/var/file/55/1055/img/312910816.pdf)。\n\n### 聯絡資訊\n- **計畫內容詢問**：國科會科國處 李蕙瑩助理研究員，電話：(02)2737-7559\n- **系統操作問題**：國科會資訊系統服務專線，電話：0800-212-058、(02)2737-7590、7591、7592\n- **校內承辦人**：研發處學術推展中心 高凱欣，電話：02-2733-3141 #7546，Email：kcc1031@mail.ntust.edu.tw"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p style=\"margin-bottom:10px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">【NSTC計畫徵求】「2027年臺德(NSTC-DAAD)青年暑期營計畫」，請於2026年1月18日(一)下午5時前完成線上申請，逾期不予受理，請查照。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><span style=\"color:#333333\"></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px; text-align:start; -webkit-text-stroke-width:0px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"box-sizing:border-box\"><span style=\"font-variant-ligatures:normal\"><span style=\"font-variant-caps:normal\"><span style=\"orphans:2\"><span style=\"widows:2\"><span style=\"text-decoration-thickness:initial\"><span style=\"text-decoration-style:initial\"><span style=\"text-decoration-color:initial\"><span style=\"word-spacing:0px\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:標楷體\"><span style=\"color:#333333\"></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">說明：</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><span style=\"color:#333333\"></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px; text-align:start; -webkit-text-stroke-width:0px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"box-sizing:border-box\"><span style=\"font-variant-ligatures:normal\"><span style=\"font-variant-caps:normal\"><span style=\"orphans:2\"><span style=\"widows:2\"><span style=\"text-decoration-thickness:initial\"><span style=\"text-decoration-style:initial\"><span style=\"text-decoration-color:initial\"><span style=\"word-spacing:0px\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">一、依國科會與德國學術交流總署(DAAD)簽署之「青年暑期營合作備忘錄」辦理。</span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">二、旨揭計畫提供雙方年輕學子暑期赴對方大學或研究機構研習之機會，赴德學員須為非人文社會領域科系且研習期間仍在學之碩、博士班學生，並能於116年暑期(7月至9月)赴德國研習者。</span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">三、本項徵求計畫案業同步公告於國科會網站，有意申請者應依說明於線上填寫及上傳送出。</span></span><span class=\"MsoHyperlink\" style=\"color:#467886\"><span style=\"text-decoration:underline\"><span lang=\"EN-US\" style=\"font-family:標楷體\"><span style=\"color:#0563c1\"><a href=\"https://rd-r.ntust.edu.tw/var/file/55/1055/img/413945039.pdf\" rel=\"noopener noreferrer\" style=\"color:#467886; text-decoration:underline\" target=\"_blank\" title=\"申請須知(另開新視窗)\"><span lang=\"EN-US\" style=\"color:#0563c1\">申請須知詳如附件</span></a></span></span></span></span><span style=\"font-family:標楷體\"><span style=\"color:#333333\">。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><span style=\"color:#333333\"></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:標楷體\"><span style=\"color:#333333\">四、本案聯絡人：</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><span style=\"color:#333333\"></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px; text-align:start; -webkit-text-stroke-width:0px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"box-sizing:border-box\"><span style=\"font-variant-ligatures:normal\"><span style=\"font-variant-caps:normal\"><span style=\"orphans:2\"><span style=\"widows:2\"><span style=\"text-decoration-thickness:initial\"><span style=\"text-decoration-style:initial\"><span style=\"text-decoration-color:initial\"><span style=\"word-spacing:0px\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:標楷體\"><span style=\"color:#333333\">(</span></span><span style=\"font-family:標楷體\"><span style=\"color:#333333\">一)相關計畫內容詢問，請洽國科會科國處李蕙瑩助理研究員，電話：(02)2737-7559。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><span style=\"color:#333333\"></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>\n\n<p style=\"margin-bottom:10px; text-align:start; -webkit-text-stroke-width:0px\"><span style=\"font-size:12pt\"><span style=\"background:white\"><span style=\"box-sizing:border-box\"><span style=\"font-variant-ligatures:normal\"><span style=\"font-variant-caps:normal\"><span style=\"orphans:2\"><span style=\"widows:2\"><span style=\"text-decoration-thickness:initial\"><span style=\"text-decoration-style:initial\"><span style=\"text-decoration-color:initial\"><span style=\"word-spacing:0px\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:標楷體\"><span style=\"color:#333333\">(</span></span><span style=\"font-family:標楷體\"><span style=\"color:#333333\">二)有關系統操作問題，請洽國科會資訊系統服務專線，電話：0800-212-058，(02)2737-7590、7591、7592。</span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span class=\"MsoHyperlink\" style=\"color:#467886\"><span style=\"text-decoration:underline\"><span lang=\"EN-US\" style=\"font-family:標楷體\"><span style=\"color:#0563c1\"><a href=\"https://rd-r.ntust.edu.tw/var/file/55/1055/img/312910816.pdf\" rel=\"noopener noreferrer\" style=\"color:#467886; text-decoration:underline\" target=\"_blank\" title=\"來文電子檔(開新視窗)\"><span lang=\"EN-US\" style=\"color:#0563c1\">來文電子檔</span></a></span></span></span></span><span class=\"MsoHyperlink\" style=\"color:#467886\"><span style=\"text-decoration:underline\"><span lang=\"EN-US\" style=\"color:#0563c1\"></span></span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Verdana&quot;,sans-serif\">National Taiwan University of Science and Technology</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Verdana&quot;,sans-serif\">Academic Collaborative Center, Office of R&amp;D</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Verdana&quot;,sans-serif\">Kao,Kai-Hsin</span> <span lang=\"JA\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">コウ カイギン</span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span style=\"font-family:標楷體\">國立臺灣科技大學 研究發展處 學術推展中心</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span style=\"font-family:標楷體\">行政書記  高凱欣  敬上</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span style=\"font-family:標楷體\">聯絡電話：02-2733-3141#7546(分機7546)</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"><span lang=\"EN-US\" style=\"font-family:標楷體\">Email:</span> <a href=\"mailto:kcc1031@mail.ntust.edu.tw\" style=\"color:#467886; text-decoration:underline\" title=\"電子郵件(另開新視窗)\">kcc1031@mail.ntust.edu.tw</a></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:Aptos,sans-serif\"></span></span></p>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">研發處計畫業務服務中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">stud-xxxx-x</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校學生</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [
      {
        "name": "申請須知詳如附件",
        "url": "https://rd-r.ntust.edu.tw/var/file/55/1055/img/413945039.pdf",
        "size": 1182314,
        "file": "/api/v1/files/cbc0bd4a930ef89a0d43bb97e052adf807c287baf7fb95009836f3b1dda2bce0/%E7%94%B3%E8%AB%8B%E9%A0%88%E7%9F%A5%E8%A9%B3%E5%A6%82%E9%99%84%E4%BB%B6"
      },
      {
        "name": "來文電子檔",
        "url": "https://rd-r.ntust.edu.tw/var/file/55/1055/img/312910816.pdf",
        "size": 290892,
        "file": "/api/v1/files/816308c17eecdb8dda2f272b6bd9d67ea2106a1b10a2c2219a5824358bfef902/%E4%BE%86%E6%96%87%E9%9B%BB%E5%AD%90%E6%AA%94"
      }
    ],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:29:53.202769+00:00"
      }
    ],
    "cross_posts": [
      {
        "id": 321,
        "site": 1055,
        "url": "https://www.rd.ntust.edu.tw/p/406-1055-153700.php"
      }
    ],
    "cross_post_of": null
  },
  "6": {
    "id": 6,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153699.php",
    "link_item": false,
    "title": "【Forwarded Message】國立臺中教育大學教務處教學發展組辦理115學年度第1學期教師知能生成式AI系列專題講座，歡迎教職員生參加。",
    "publisher": "教務處教學發展中心",
    "day": "2026-11-13",
    "listed_on": "2026-11-13",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391"
    ],
    "tags": {
      "topic": [
        "talks-and-events"
      ],
      "audience": [
        "all-students",
        "staff"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "forwarded"
      ]
    },
    "rendition": {
      "title": "國立臺中教育大學教務處教學發展組辦理115學年度第1學期教師知能生成式AI系列專題講座，歡迎教職員生參加。",
      "summary": "國立臺中教育大學於12月8日舉辦生成式AI專題線上講座，即日起至12月4日開放全國大專院校教職員生報名。",
      "deadline": "2026-12-04",
      "markdown": "國立臺中教育大學教務處教學發展組辦理115學年度第1學期教師知能生成式AI系列專題講座，歡迎全國大專院校教職員生參加。\n\n- **活動主題**：與AI共備、共學、共創：AI賦能教學創新的無限可能\n- **活動講師**：國立臺東大學師資培育中心實習輔導組 武佳瀅組長兼教育學系副教授\n- **活動時間**：115年12月8日（星期二）下午2時至5時\n- **活動地點**：線上 Google meeting 教室（活動前將寄發教室連結至報名信箱）\n- **活動報名**：即日起至**115年12月4日（星期四）止**開放[線上報名](http://forms.gle/inGDBMgd4SPsc3gp6)\n- **參加對象**：全國大專院校教職員生\n- **研習證明**：活動全程參與者將於活動結束後核發電子研習證書\n\n聯絡人：國立臺中教育大學教務處教學發展組李小姐，電話：(04)2218-3143，信箱：ctd@mail.ntcu.edu.tw。"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p style=\"margin-bottom:11px\"><span style=\"font-family:微軟正黑體;\"><span style=\"font-size:12pt\"><span style=\"line-height:115%\"><br>\n一、活動資訊：<br>\n(一)活動主題：與AI共備、共學、共創：AI賦能教學創新的無限可能。<br>\n(二)活動講師：國立臺東大學師資培育中心實習輔導組 武佳瀅組長兼教育學系副教授。<br>\n(三)活動時間：115年12月8日(星期二)下午2時至5時。<br>\n(四)活動地點：線上Google meeting教室(活動前將寄發教室連結至報名信箱)。<br>\n(五)活動報名：即日起至115年12月4日(星期四)止開放線上報名：<a href=\"http://forms.gle/inGDBMgd4SPsc3gp6\" style=\"color:blue; text-decoration:underline\">http://forms.gle/inGDBMgd4SPsc3gp6</a><br>\n二、參加對象：全國大專院校教職員生。<br>\n三、研習證明：活動全程參與者將於活動結束後核發電子研習證書。<br>\n四、聯絡人：國立臺中教育大學教務處教學發展組李小姐，電話：(04)2218-3143，信箱：ctd@mail.ntcu.edu.tw。</span></span></span></p>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">教務處教學發展中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">muser-xx-xxxx,stud-xxxx-x</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校教職員生</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [
      {
        "name": "海報.jpg",
        "url": "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile&file=cVdEMEZ5SHEzcmQ2bzhIRGxKSmZkSkJkNHRaa0Z3MDFjMFlJcmdXSmxWYmVHYVRySnhMWExYcTNpTUpyemw0SGJzUll2SGorQVc3V01XZWdMZHJKcTRudnZkWlJadjZMSldjUDB5eDF6NkU9&fname=YkFvTFZkN2VRU1FVVXM3SmRzVVJjb252dmRaUlp2NkxKV2NQMHl4MXo2RT0=",
        "size": 401121,
        "file": "/api/v1/files/67212f6973c045db99fc9f38f9efed5005b5d253edc1447543c203625753df88/%E6%B5%B7%E5%A0%B1.jpg"
      }
    ],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:29:57.998972+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": null
  },
  "8": {
    "id": 8,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153695.php",
    "link_item": false,
    "title": "【Forwarded Message】教學實踐研究計畫中部區域基地謹訂於115年12月1日辦理「教學實踐研究計畫撰稿工作坊」，歡迎教師參加。",
    "publisher": "教務處教學發展中心",
    "day": "2026-11-13",
    "listed_on": "2026-11-13",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391"
    ],
    "tags": {
      "topic": [
        "talks-and-events",
        "research-projects"
      ],
      "audience": [
        "staff"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "forwarded"
      ]
    },
    "rendition": {
      "title": "教學實踐研究計畫中部區域基地謹訂於115年12月1日辦理「教學實踐研究計畫撰稿工作坊」，歡迎教師參加。",
      "summary": "教學實踐研究計畫撰稿工作坊12月1日於靜宜大學舉行，教師可於11月26日13:00前報名。",
      "deadline": "2026-11-26",
      "markdown": "教學實踐研究計畫中部區域基地為協助教育部推動教學實踐研究計畫，跨校共構教學實踐支持網絡，舉辦教師實作工坊，歡迎教師參加。\n\n- **活動名稱**：教學實踐研究計畫撰稿工作坊\n- **時間**：115年12月1日（星期二）13:00–17:00\n- **講師**：國立高雄師範大學 科學教育暨環境教育研究所 黃琴扉 教授\n- **地點**：靜宜大學宜園3樓 iDO培力基地\n- **報名方式**：請至[活動報名網頁](https://reurl.cc/VnAaaQ)報名，**即日起至11月26日（星期四）13:00止**\n- **名額**：限額30名\n- **研習證明**：全程參與者將頒予中部區域基地研習證明\n\n### 活動聯絡人\n- 靜宜大學 教務處 陳宥臻：04-26328001#11143 / cyc11143@pu.edu.tw\n- 靜宜大學 教務處 教學發展中心 熊若婷助理：04-26328001#11137 / bear0822@pu.edu.tw"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p style=\"margin-bottom:11px\"><span style=\"font-family:微軟正黑體;\"><span style=\"font-size:12pt\"><span style=\"line-height:115%\"><br>\n一、旨揭活動目的係為協助教育部推動教學實踐研究計畫，希冀透過區域基地學校辦理之各類活動，跨校共構教學實踐支持網絡，推動教師支持系統，落實學生為核心之教學實踐研究之任務。<br>\n二、教師實作工坊相關資訊：<br>\n(一)名稱：「教學實踐研究計畫撰稿工作坊」。<br>\n(二)時間：115年12月1日（星期二）下午1時至下午5時。<br>\n(三)講師：國立高雄師範大學 科學教育暨環境教育研究所 黃琴扉 教授。<br>\n(四)地點：靜宜大學宜園3樓 iDO培力基地。<br>\n(五)報名網址：<a href=\"https://reurl.cc/VnAaaQ\" style=\"color:blue; text-decoration:underline\">https://reurl.cc/VnAaaQ</a>，即日起至11月26日（星期四）下午1時止。<br>\n(六)人數：限額30名。<br>\n(七)全程參與者，將頒予中部區域基地研習證明。<br>\n三、活動聯絡人：<br>\n(一)靜宜大學 教務處 陳宥臻04-26328001#11143 cyc11143@pu.edu.tw<br>\n(二)靜宜大學 教務處 教學發展中心 熊若婷助理04-26328001#11137 bear0822@pu.edu.tw</span></span></span></p></div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">教務處教學發展中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">muser-px-xxxx,muser-fx-xxxx,muser-yx-xxxx</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校教師</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [
      {
        "name": "海報.pdf",
        "url": "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile&file=QjVkUGRlUmVUYVVodUFhWjBIU293SkJkNHRaa0Z3MDFjMFlJcmdXSmxWYklvUFhzMkN2eWhmY1RnYjdZQXJnWlVsdCthVG40S0ZadW0wakJpNVN6Z0RMcHdWVnQxbTNyamZBbkNUZHhsMVk9&fname=enZ3d1cvZ0RsZC9kMU9jUnNqWDRpRExwd1ZWdDFtM3JqZkFuQ1RkeGwxWT0=",
        "size": 804493,
        "file": "/api/v1/files/dfa8df87b1d543d97ef5e61d9c979a06272ab14ebc01d849401fabdfc507ea73/%E6%B5%B7%E5%A0%B1.pdf"
      }
    ],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:30:02.887955+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": null
  },
  "10": {
    "id": 10,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153453.php",
    "link_item": false,
    "title": "【NSTC計畫徵求】國科會徵件一覽表 Forwarded Message",
    "publisher": "研發處計畫業務服務中心",
    "day": "2026-11-13",
    "listed_on": "2026-11-13",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391"
    ],
    "tags": {
      "topic": [],
      "audience": [],
      "nature": [],
      "source": []
    },
    "rendition": null,
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p>國科會徵件一覽表【<a href=\"https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw\" rel=\"noopener noreferrer\" target=\"_blank\" title=\"國科會徵件一覽表網址連結(另開新視窗)\"><span style=\"color:#2980b9;\">連結</span></a>】 Forwarded Message <span style=\"color:#2980b9;\"></span></p>\n\n<p>【研發處網站/計畫徵求/國科會計畫徵求/國科會徵件一覽表<a href=\"http:// https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw\" rel=\"noopener noreferrer\" target=\"_blank\" title=\"國科會徵件一覽表網址連結(另開新視窗)\"> <span style=\"color:#2980b9;\"></span></a><a href=\"https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw\" rel=\"noopener noreferrer\" target=\"_blank\" title=\"國科會徵件一覽表網址連結(另開新視窗)\"><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\">https://www.rd.ntust.edu.tw/p/404-1055-81503.php?Lang=zh-tw</span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span></a>】</p>\n\n<p> The calls for the proposals by the National Science and Technology Council (NSTC) are summarized on the ORD website. The link is as follows:<span style=\"color:#0477c3;\"> </span><a href=\"https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw\" rel=\"noopener noreferrer\" target=\"_blank\" title=\"國科會徵件一覽表網址連結(另開新視窗)\"><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\">https://www.rd.ntust.edu.tw/p/404-1055-81503.php?Lang=zh-tw</span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span><span style=\"color:#0477c3;\"></span></a></p></div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">研發處計畫業務服務中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">stud-xxxx-x,muser-xx-xxxx</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校教職員工生</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:30:07.750876+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": null
  },
  "11": {
    "id": 11,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153676.php",
    "link_item": false,
    "title": "【Forwarded Message】教學實踐南區基地謹訂於115年11月20日（五）辦理115年度教學實踐研究計畫南區基地「跨校教師社群成果交流會暨共識會議」，歡迎教師參加。",
    "publisher": "教務處教學發展中心",
    "day": "2026-11-13",
    "listed_on": "2026-11-13",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391"
    ],
    "tags": {
      "topic": [
        "talks-and-events"
      ],
      "audience": [
        "staff"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "forwarded"
      ]
    },
    "rendition": {
      "title": "教學實踐南區基地謹訂於115年11月20日（五）辦理115年度教學實踐研究計畫南區基地「跨校教師社群成果交流會暨共識會議」，歡迎教師參加。",
      "summary": "國立中山大學11月20日線上舉辦跨校教師社群成果交流會暨共識會議，請於11月18日前報名。",
      "deadline": "2026-11-18",
      "markdown": "115年度教育部教學實踐研究區域基地計畫為發展跨校教師支持網絡並建置區域基地跨校支持系統，鼓勵教師組成跨校教師社群、落實創新教學並投入教學學術研究（SoTL）。為促進社群交流及展現執行成果，國立中山大學將辦理成果交流會暨共識會議，歡迎教師參加。\n\n### 活動資訊\n- 主題：115年度南區基地國立中山大學跨校教師社群期末成果交流會暨共識會議\n- 時間：115年11月20日（五）14:00–16:10（13:30開始報到）\n- 地點：Google Meet 線上研習（報名成功後將另行寄送連結網址）\n- 參加對象：各公私立大專校院教師及對本活動有興趣參與者\n\n### 報名資訊\n- 報名期限：即日起至 **115年11月18日（三）** 止（限額100人，額滿即停止受理）\n- 報名方式：請至[線上報名系統](https://pse.is/9us7d6)報名\n\n### 聯絡資訊\n- 聯絡人：國立中山大學教務處教學發展與資源中心 吳助理\n- 電話：07-5252000 分機 2163"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p style=\"margin-bottom:11px\"><span style=\"font-family:微軟正黑體;\"><span style=\"font-size:12pt\"><span style=\"line-height:115%\"><br>\n一、115年度教育部教學實踐研究區域基地計畫為發展跨校教師支持網絡並建置區域基地跨校支持系統，以教學實踐研究計畫為主題，鼓勵教師組成跨校教師社群，落實教師創新教學，並鼓勵投入教學學術研究(SoTL)，達到提升教師教學研究能量與品質。<br>\n二、為促進社群交流機會及展現本年度跨校教師社群執行成果，國立中山大學將辦理成果交流會暨共識會議，誠摰邀請大專校院教師共襄盛舉。<br>\n三、活動資訊<br>\n(一)主題：115年度南區基地國立中山大學跨校教師社群期末成果交流會暨共識會議<br>\n(二)時間：115年11月20日(五) 下午14:00-16:10 (13:30開始報到)<br>\n(三)地點：Google meet線上研習(報名成功後，將另行寄送連結網址)。<br>\n(四)參加對象：各公私立大專校院教師及對本活動有興趣參與者。<br>\n四、報名時間：即日起截至115年11月18日(星期三)，人數限額100 人，額滿即停止受理報名。<br>\n五、報名連結：<a href=\"https://pse.is/9us7d6\" style=\"color:blue; text-decoration:underline\">https://pse.is/9us7d6</a><br>\n六、本案聯絡人：國立中山大學教務處教學發展與資源中心吳助理，電話07-5252000分機2163。</span></span></span></p>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">教務處教學發展中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">muser-px-xxxx,muser-fx-xxxx,muser-yx-xxxx</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校教師</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [
      {
        "name": "海報.png",
        "url": "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile&file=RTA0YlpEUVMrZ0xPZGRKTFFqWFArZWFpVTFaNHdXMEJxbjVtUFYxT0Q2bVc4TS9RanVDSlVrb1lFeGE1djBqRGFxN1NZT2hmRUVQUEQzVllSbndVcVludnZkWlJadjZMSldjUDB5eDF6NkU9&fname=WGYyOGxxRXpzN1d2VFhGYzlndXZHb252dmRaUlp2NkxKV2NQMHl4MXo2RT0=",
        "size": 8269382,
        "file": null
      }
    ],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:30:10.543242+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": null
  },
  "14": {
    "id": 14,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153650.php",
    "link_item": false,
    "title": "【Forwarded Message】國立高雄大學 創新學院辦理「AI工具融入教學與研究」系列教師增能研習資訊，敬請惠予公告並協助宣傳，歡迎教職員生參加。",
    "publisher": "教務處教學發展中心",
    "day": "2026-11-12",
    "listed_on": "2026-11-12",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391"
    ],
    "tags": {
      "topic": [
        "talks-and-events"
      ],
      "audience": [
        "all-students",
        "staff"
      ],
      "nature": [
        "information"
      ],
      "source": [
        "forwarded"
      ]
    },
    "rendition": {
      "title": "國立高雄大學 創新學院辦理「AI工具融入教學與研究」系列教師增能研習資訊，敬請惠予公告並協助宣傳，歡迎教職員生參加。",
      "summary": "國立高雄大學辦理「AI工具融入教學與研究」線上研習，歡迎教職員生報名參加。",
      "deadline": null,
      "markdown": "國立高雄大學創新學院辦理「AI工具融入教學與研究」教師增能研習，採**線上直播**方式進行，開放校內外教職員及公務人員報名參與。\n\n### 場次一\n- 時間：115年12月14日（一）13:00-16:00\n- 講師：沃克資訊有限公司 黃信溢老師（茶米老師）\n- 主題：研究開外掛！ Gemini Notebook AI實戰大解密\n- 報名方式：[場次一線上報名](https://forms.gle/iBgA22pY15QSCtSq6)\n\n### 場次二\n- 時間：115年12月16日（三）13:00-15:30\n- 講師：逢甲大學人文社會學院 曾智義專任助理教授\n- 主題：AI工具與學術研究\n- 報名方式：[場次二線上報名](https://forms.gle/L2CjTJ5Sa8uCUcZV8)\n\n### 聯絡資訊\n- 聯絡人：國立高雄大學 創新學院 王小姐\n- 電話：(07)591-6261\n- Email：huifang817@nuk.edu.tw"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p style=\"margin-bottom:11px\"><span style=\"font-family:微軟正黑體;\"><span style=\"font-size:12pt\"><span style=\"line-height:115%\"><br>\n一、為提升教師運用AI工具能力，促進創新教學與研究發展，國立高雄大學 創新學院辦理旨揭教師增能研習，採線上直播方式進行，開放校內外教職員及公務人員報名參與。<br>\n二、場次一研習資訊如下：<br>\n(一)時間：115年12月14日(一)13:00-16:00<br>\n(二)講師：沃克資訊有限公司黃信溢老師(茶米老師)<br>\n(三)主題：研究開外掛！ Gemini Notebook AI實戰大解密<br>\n(四)線上報名網址：<a href=\"https://forms.gle/iBgA22pY15QSCtSq6\" style=\"color:blue; text-decoration:underline\">https://forms.gle/iBgA22pY15QSCtSq6</a><br>\n三、場次二研習資訊如下：<br>\n(一)時間：115年12月16日(三)13:00-15:30<br>\n(二)講師：逢甲大學人文社會學院曾智義專任助理教授<br>\n(三)主題：AI工具與學術研究<br>\n(四)線上報名網址：<a href=\"https://forms.gle/L2CjTJ5Sa8uCUcZV8\" style=\"color:blue; text-decoration:underline\">https://forms.gle/L2CjTJ5Sa8uCUcZV8</a><br>\n四、聯絡人：國立高雄大學 創新學院王小姐，電話(07)591-6261，Email：huifang817@nuk.edu.tw</span></span></span></p>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">教務處教學發展中心</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">muser-xx-xxxx,stud-xxxx-x</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全校教職員生</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [
      {
        "name": "12.14海報.jpg",
        "url": "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile&file=Ums4ckNOcG91SHJod0x3dTRZQmQvZGJCY3NHc1VJa1VibHAybEc5VlhGLzdPNDBENU44aFBxaWhkYVJSemhFY2ZTY3ByTVBpUkFaVXE2QlZvNDVPNkNsVUgrSVRZWEE2WlBKeEFISDFaQms9&fname=QWlGUW5RNFo3Y1FNV3lpakkzQjFMbi9TcjdINzFhc1htdU0wSm8rd3dyNHBWQi9pRTJGd09tVHljUUJ4OVdRWg==",
        "size": 1187660,
        "file": "/api/v1/files/4381c1be149ef4af5ade459f84e08e87c3175fe074112690b0cdb5c64a50ee06/12.14%E6%B5%B7%E5%A0%B1.jpg"
      },
      {
        "name": "12.16海報.jpg",
        "url": "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile&file=Ums4ckNOcG91SHJod0x3dTRZQmQvUThqcXF1WHBYbXJaRGxzTWc0SnhrNWtOSitUeWIwSC9TTER1N2RCS1ZvSkZvSUpKMk9TaVgweU1LbFJNeXBqOUNsVUgrSVRZWEE2WlBKeEFISDFaQms9&fname=eTFVeUNkaDU2YThDaGdETlh6MTNoWC9TcjdINzFhc1htdU0wSm8rd3dyNHBWQi9pRTJGd09tVHljUUJ4OVdRWg==",
        "size": 1344761,
        "file": "/api/v1/files/c37cb71d3b7d8f8dc511c70a6c48390481bbf928fd29749b78e29c3be5a0aeff/12.16%E6%B5%B7%E5%A0%B1.jpg"
      }
    ],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:30:19.131026+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": null
  },
  "16": {
    "id": 16,
    "site": 1045,
    "unit": "全校公佈欄",
    "url": "https://bulletin.ntust.edu.tw/p/406-1045-153626.php",
    "link_item": false,
    "title": "慶祝圖書館大樓50歲~ 敬邀您參與解開時光密碼，抽禮券！還能在留言牆寫下給圖書館的祝福！",
    "publisher": "圖書館",
    "day": "2026-11-12",
    "listed_on": "2026-11-12",
    "first_seen_at": "2026-11-15T05:12:53.420804+00:00",
    "withdrawn_at": null,
    "boards": [
      "1045-1391",
      "1049-1"
    ],
    "tags": {
      "topic": [
        "talks-and-events"
      ],
      "audience": [
        "all-students",
        "staff"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "on-campus"
      ]
    },
    "rendition": {
      "title": "慶祝圖書館大樓50歲~ 敬邀您參與解開時光密碼，抽禮券！還能在留言牆寫下給圖書館的祝福！",
      "summary": "圖書館50週年活動自11/11至11/25止，本校教職員工生可參加「時空檔案」線上解謎抽禮券，或至一樓留言牆寫下祝福。",
      "deadline": "2026-11-25",
      "markdown": "### 活動一：邀請你打開「時空檔案」\n\n跟著 3 道簡單謎題，解開圖書館的時光密碼！完成挑戰，即有機會抽中禮券。\n\n- 活動期間：**2026/11/11 (Wed) ~ 11/25 (Wed)**\n- 活動對象：本校教職員工生\n- 活動方式：進入[「時空檔案」活動網站](https://tiger-ynb6ns.my.canva.site/50thlib)，完成 3 道題目並填寫資料\n- 獎項：超商禮券 100 元，共 20 名\n- 得獎公布：**12/1 (Tue) 前**於圖書館首頁「最新消息」公布中獎名單\n\n### 活動二：給50歲的圖書館，一句話\n\n在圖書館大樓 50 歲的這一年，歡迎寫下祝福、回憶、小小抱怨，或對未來圖書館的期待。\n\n- 留言地點：圖書館一樓新書展示區 — 50 歲留言牆\n\n![活動海報](https://bulletin.ntust.edu.tw/var/file/45/1045/img/2535/396338505.png)\n\n### 注意事項\n\n1. 中獎名單公告後，將以 Email 通知及網頁最新消息公告。中獎者請攜帶本人學生證／教職員證，至圖書館領取獎品。\n2. 每位參加者僅限一次抽獎機會，不得重複領獎。\n3. 逾領獎期限仍未領取獎品者，視同放棄領獎資格；中獎者不得以未收到通知為由要求本館補發獎品。\n4. 如遇獎品缺貨或因不可抗力因素致無法提供原定獎品，本館得以等值商品替代之，中獎者不得要求折現或更換其他商品。\n5. 獎品所得依國內稅法辦理；外籍中獎人須配合稅務申報，並提供護照、居留證等身分證明文件影本。"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\n\t\t\n\t\n\t \n\t\t<div class=\"meditor\"><p><span style=\"font-size:12pt\"><span style=\"font-family:新細明體,serif\"><b><span style=\"font-size:16.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"><br>\n圖書館大樓50歲了！一起翻閱我們的時光</span></span></b><br>\n<b><span style=\"font-size:10.5pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">解開50年的時空檔案，留下一句給圖書館的話</span></span></b><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:新細明體,serif\"> </span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-size:10.5pt\"><span style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">🎉</span></span> <b><span style=\"background:aqua\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">活動一　邀請你打開「時空檔案」</span></span></b><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span><br>\n<span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">跟著3道簡單謎題，解開圖書館的時光密碼！完成挑戰，即有機會抽中禮券！</span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"> <span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">🗓</span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">️ </span><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">活動期間：<b>11/11 (Wed) ~ 11/25 (Wed) </b></span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">👥</span> <span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">活動對象：本校教職員工生</span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">🎯</span> <span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">活動方式：進入<b><span lang=\"EN-US\" style=\"color:blue\"><a href=\"https://tiger-ynb6ns.my.canva.site/50thlib\" style=\"color:#467886; text-decoration:underline\" target=\"_blank\">「時空檔案」活動網站</a></span></b>，完成3道題目並填寫資料</span><br>\n<span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">🎁</span> <span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">獎項：超商禮券100元，共20名</span><br>\n<span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">💰</span> <span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">得獎公布：12/1(Tue)前於圖書館首頁「最新消息」公布中獎名單</span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"> </span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"> </span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-size:10.5pt\"><span style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">🎉</span></span> <b><span style=\"background:aqua\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">活動二　給50歲的圖書館，一句話</span></span></b><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">在圖書館大樓50歲的這一年，你想對圖書館說什麼？<br>\n一句祝福、一段回憶、一個小小抱怨，<br>\n或者，希望未來的圖書館變成什麼模樣……都歡迎寫下來。</span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"line-height:15.0pt\"><span style=\"font-family:新細明體,serif\"><span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">📍</span><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">留言地點｜圖書館一樓新書展示區--50歲留言牆</span></span></span></span></p>\n\n<p><span style=\"font-size:12pt\"><span style=\"font-family:新細明體,serif\"><img alt=\"\" height=\"331\" src=\"/var/file/45/1045/img/2535/396338505.png\" width=\"500\"><br>\n<br>\n<span lang=\"EN-US\" style=\"font-family:&quot;Segoe UI Emoji&quot;,sans-serif\">⚠</span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">️</span><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">注意事項：</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></p>\n\n<ol>\n\t<li><span style=\"font-size:12pt\"><span style=\"tab-stops:list 36.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">中獎名單公告後，將以Email通知及網頁最新消息公告。中獎者請攜帶本人學生證/教職員證，至圖書館領取獎品。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></li>\n\t<li><span style=\"font-size:12pt\"><span style=\"tab-stops:list 36.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">每位參加者僅限一次抽獎機會，不得重複領獎。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></li>\n\t<li><span style=\"font-size:12pt\"><span style=\"tab-stops:list 36.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">逾領獎期限仍未領取獎品者，視同放棄領獎資格；中獎者不得以未收到通知為由要求本館補發獎品。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></li>\n\t<li><span style=\"font-size:12pt\"><span style=\"tab-stops:list 36.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">如遇獎品缺貨或因不可抗力因素致無法提供原定獎品，本館得以等值商品替代之，中獎者不得要求折現或更換其他商品。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></li>\n\t<li><span style=\"font-size:12pt\"><span style=\"tab-stops:list 36.0pt\"><span style=\"font-family:新細明體,serif\"><span style=\"font-size:10.0pt\"><span style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\">獎品所得依國內稅法辦理；外籍中獎人須配合稅務申報，並提供護照、居留證等身分證明文件影本。</span></span><span lang=\"EN-US\" style=\"font-family:&quot;微軟正黑體&quot;,sans-serif\"></span></span></span></span></li>\n</ol>\n</div>\n\t\n\t\n\t<div class=\"mattr\">\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">發佈單位: </span>\n\t\t\t<span class=\"mattr-val\">圖書館</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送群組: </span>\n\t\t\t<span class=\"mattr-val\">ntust-all</span>\n\t\t</div>\n\t\t\n\t\t<div class=\"mattr-item\">\n\t\t\t<span class=\"mattr-name\">寄送對象: </span>\n\t\t\t<span class=\"mattr-val\">全體教職員工生</span>\n\t\t</div>\n\t\t\n\t</div>\n\t\n\t\n</div>",
    "attachments": [],
    "revisions": [
      {
        "fetched_at": "2026-11-15T05:30:24.765719+00:00"
      }
    ],
    "cross_posts": [
      {
        "id": 32,
        "site": 1049,
        "url": "https://library.ntust.edu.tw/p/406-1049-153618.php"
      }
    ],
    "cross_post_of": null
  },
  "615": {
    "id": 615,
    "site": 1000,
    "unit": "官網",
    "url": "https://www.ntust.edu.tw/p/406-1000-144278.php",
    "link_item": false,
    "title": "50周年校慶英文專刊",
    "publisher": null,
    "day": "2026-02-10",
    "listed_on": "2026-02-10",
    "first_seen_at": "2026-11-15T05:15:13.533528+00:00",
    "withdrawn_at": "2026-11-15T05:56:01.730421+00:00",
    "boards": [
      "1000-168"
    ],
    "tags": {
      "topic": [],
      "audience": [],
      "nature": [],
      "source": []
    },
    "rendition": null,
    "body_html": null,
    "attachments": [],
    "revisions": [],
    "cross_posts": [],
    "cross_post_of": null
  },
  "794": {
    "id": 794,
    "site": 1007,
    "unit": "專利研究所、智慧財產權學士學位學程",
    "url": "https://patent.ntust.edu.tw/p/406-1007-153457.php",
    "link_item": false,
    "title": "【招生訊息】臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
    "publisher": null,
    "day": "2026-11-06",
    "listed_on": null,
    "first_seen_at": "2026-11-15T05:16:19.547898+00:00",
    "withdrawn_at": null,
    "boards": [],
    "tags": {
      "topic": [
        "talks-and-events",
        "admissions",
        "free-food"
      ],
      "audience": [
        "public"
      ],
      "nature": [
        "action-required"
      ],
      "source": [
        "on-campus"
      ]
    },
    "rendition": {
      "title": "臺科大專利所116學年度碩士在職專班招生說明會：115/11/22(日)上午10:00-11:00, 歡迎踴躍報名！",
      "summary": "臺科大專利所116學年度碩士在職專班招生說明會將於115年11月22日舉行，實體參與提供西點餐盒，網路報名至12月10日止。",
      "deadline": "2026-12-10",
      "markdown": "臺科大專利所 116 學年度碩士在職專班招生說明會資訊如下：\n\n- **日期：**115年11月22日（週日），開放同步遠距參加\n- **時間：**上午 10:00 - 11:00\n- **地點：**本校研揚大樓八樓（TR-829）\n- **遠距參加：**[遠距參加網址](https://meet.google.com/gcr-cxec-apf)\n- **報名連結：**[報名招生說明會](https://forms.gle/GPqQa5mFhB1Mf3dA6)\n- **實體參與福利：**提供西點餐盒一份\n\n打造跨域競爭優勢，培養「技術 x 法律 x 管理」專業智慧財產人才。\n\n- [觀看 116 學年度臺科大專利所碩士在職專班招生宣傳影片](https://youtu.be/m9DPvXdSeJc)\n\n### 碩士在職專班招生資訊\n- **網路報名時間：**115年11月27日（星期五）上午 9:00 起至 **115年12月10日（星期四）下午 5:00 止**\n- [臺科大 116 學年度碩士在職專班招生資訊](https://www.admission.ntust.edu.tw/p/405-1052-153258,c8737.php?Lang=zh-tw)"
    },
    "body_html": "<div class=\"mpgdetail\">\n\t\n\t\t\n \t\t\n\t\t\n\t\t\n\t\t\n\t\t\n\t\n\t\n   <div class=\"meditor\"><h1>臺科大專利所 116 學年度碩士在職專班招生說明會</h1>\n\n\n<ul>\n\t<li><strong>日期：</strong>115年11月22日（週日）開放同步遠距參加。</li>\n\t<li><strong>遠距參加網址: </strong><a href=\"https://meet.google.com/gcr-cxec-apf\" title=\"116學年度招說會遠距網址\"> <span style=\"font-size:12pt\"><span style=\"line-height:115%\"><span style=\"font-family:Aptos,sans-serif\">https://meet.google.com/gcr-cxec-apf</span></span></span></a></li>\n\t<li><strong>時間：</strong>上午 10:00 - 11:00</li>\n\t<li><strong>地點：</strong>本校研揚大樓八樓(TR-829)</li>\n\t<li><strong>報名招生說明會：</strong><a href=\"https://forms.gle/GPqQa5mFhB1Mf3dA6\" title=\"116學年度臺科大專利所碩專班招說會報名表\">https://forms.gle/GPqQa5mFhB1Mf3dA6</a></li>\n\t<li><strong>實體參與提供西點餐盒一份！</strong></li>\n</ul>\n\n\n<p> </p>\n\n\n<p>打造跨域競爭優勢 成就無可取代的你<br>\n技術 x 法律 x 管理<br>\n培養專業的智慧財產人才</p>\n\n\n<p><a href=\"https://youtu.be/m9DPvXdSeJc\" title=\"116碩專班招生宣傳影片\">觀看 116 學年度臺科大專利所碩士在職專班招生宣傳影片（YouTube，另開新視窗） </a></p>\n\n<hr>\n<h2 id=\"master-admission-title\">臺科大專利所碩士在職專班招生資訊</h2>\n\n<p><strong>網路報名時間：</strong>115年11月27日（星期五）上午 9:00 起至 115年12月10日（星期四）下午 5:00 止</p>\n\n<p><strong>本校招生資訊：</strong><a href=\"https://www.admission.ntust.edu.tw/p/405-1052-153258,c8737.php?Lang=zh-tw\" title=\"116臺科大碩專班招生資訊\"> 臺科大 116 學年度碩士在職專班招生資訊（另開新視窗）</a></p>\n</div>\n\t\n\t\n\t\n</div>",
    "attachments": [],
    "revisions": [
      {
        "fetched_at": "2026-11-15T06:03:53.823916+00:00"
      }
    ],
    "cross_posts": [],
    "cross_post_of": 1
  },
  "2533": {
    "id": 2533,
    "site": 1111,
    "unit": "產學創新學院、先進半導體科技研究所",
    "url": "https://innc.ntust.edu.tw/p/450-1111-152943,c0.php?Lang=zh-tw",
    "link_item": true,
    "title": "全球量子競賽升溫! 外商來台設廠 電子大廠卡位搶人才｜TVBS新聞(本所巫朝陽老師受訪)",
    "publisher": null,
    "day": "2026-11-15",
    "listed_on": null,
    "first_seen_at": "2026-11-15T05:29:23.630334+00:00",
    "withdrawn_at": null,
    "boards": [
      "1111-2239"
    ],
    "tags": {
      "topic": [],
      "audience": [],
      "nature": [],
      "source": []
    },
    "rendition": null,
    "body_html": null,
    "attachments": [],
    "revisions": [],
    "cross_posts": [],
    "cross_post_of": null
  }
} satisfies Record<number, Article>;
