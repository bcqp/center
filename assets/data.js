/*
  BIQEP Policy Briefs — site data.
  This is the ONLY file that changes in the weekly loop (plus a new brief page).

  Rules:
  - A series gets status "verified" only after its value has been checked against
    the original official release. Record the source URL and the retrieval date.
  - Anything not yet checked stays "pending" with value null. Never fill a gap with a guess.
  - A brief is listed as "published" only after the author has approved it.
*/
window.BIQEP = {
  updated: "2026-11-14",

  series: [
    {
      id: "cpi_p2p",
      name: "CPI inflation, point to point",
      topic: "Inflation",
      unit: "%",
      status: "verified",
      latest: { period: "Sep 2026", value: 8.34 },
      history: [
        { period: "Aug 2026", value: 8.26 },
        { period: "Sep 2025", value: 8.36 }
      ],
      source: "Bangladesh Bureau of Statistics (BBS), published by Bangladesh Bank",
      url: "https://www.bb.org.bd/en/index.php/econdata/inflation",
      retrieved: "2026-11-14",
      note: "CPI base 2021-22 = 100 from April 2023."
    },
    {
      id: "cpi_12m",
      name: "CPI inflation, 12-month average",
      topic: "Inflation",
      unit: "%",
      status: "verified",
      latest: { period: "Sep 2026", value: 8.65 },
      history: [
        { period: "Aug 2026", value: 8.66 },
        { period: "Sep 2025", value: 9.45 }
      ],
      source: "Bangladesh Bureau of Statistics (BBS), published by Bangladesh Bank",
      url: "https://www.bb.org.bd/en/index.php/econdata/inflation",
      retrieved: "2026-11-14",
      note: "CPI base 2021-22 = 100 from April 2023."
    },
    {
      id: "policy_rate",
      name: "Policy rate (repo)",
      topic: "Monetary policy",
      unit: "%",
      status: "pending",
      latest: null,
      source: "Bangladesh Bank",
      note: "Sources disagree (10.00% in press reports, 9.50% in a policy statement). Awaiting the original Bangladesh Bank announcement."
    },
    {
      id: "cpi_food",
      name: "Food inflation, point to point",
      topic: "Inflation",
      unit: "%",
      status: "pending",
      latest: null,
      source: "Bangladesh Bureau of Statistics (BBS)",
      note: "To be taken from the BBS monthly CPI release."
    },
    {
      id: "cpi_nonfood",
      name: "Non-food inflation, point to point",
      topic: "Inflation",
      unit: "%",
      status: "pending",
      latest: null,
      source: "Bangladesh Bureau of Statistics (BBS)",
      note: "To be taken from the BBS monthly CPI release."
    },
    {
      id: "wage_index",
      name: "Wage rate index, growth",
      topic: "Labor and wages",
      unit: "%",
      status: "pending",
      latest: null,
      source: "Bangladesh Bureau of Statistics (BBS)",
      note: "To be taken from the BBS wage rate index release."
    },
    {
      id: "bdt_usd",
      name: "Exchange rate, BDT per USD",
      topic: "External sector",
      unit: "BDT",
      status: "pending",
      latest: null,
      source: "Bangladesh Bank",
      note: "To be taken from the Bangladesh Bank exchange rate page."
    }
  ],

  briefs: [
    {
      slug: "inflation-above-8",
      title: "Why is inflation still above 8%?",
      topic: "Inflation",
      status: "in-preparation",
      type: "Data note",
      date: "2026-11",
      summary: "Headline inflation has barely moved in a year while the 12-month average has fallen. This note sets out the verified figures; the full brief will test what drives the gap using food and non-food prices, wages, the exchange rate and the policy rate."
    }
  ],

  topics: [
    { name: "Inflation", slug: "inflation", text: "Price dynamics, food and non-food inflation, and expectations." },
    { name: "Monetary policy", slug: "monetary-policy", text: "Policy rates, transmission to lending and the exchange rate." },
    { name: "Public finance", slug: "public-finance", text: "Revenue, spending, deficits and debt sustainability." },
    { name: "Labor and wages", slug: "labor-wages", text: "Employment, real wages and the informal economy." },
    { name: "External sector", slug: "external-sector", text: "Exchange rate, remittances, reserves and trade." },
    { name: "Finance and credit", slug: "finance-credit", text: "Bank lending, interest rates and financial stability." },
    { name: "Climate and energy", slug: "climate-energy", text: "Energy prices, green finance and climate risk." }
  ]
};
