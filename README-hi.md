# dsh-gongwen-word-check — सरकारी दस्तावेज़ रजिस्टर के प्रारूप-तत्वों की जाँच

`dsh-gongwen-word-check` एक सरकारी दस्तावेज़ रजिस्टर पढ़ता है — जारी किए गए प्रत्येक दस्तावेज़ की एक पंक्ति — और उस रजिस्टर में दर्ज पाठ की तुलना एक संस्करणबद्ध नियम-पैक से करता है: क्या `发文字号` «机关代字〔年份〕序号» के रूप में है और वर्ष षट्कोणीय कोष्ठक 〔〕 में है, क्या `成文日期` दिनांक के रूप में पढ़ी जा सकती है और जाँच के दिन से बाद की नहीं है, क्या `文种` आपकी अपनी इकाई द्वारा कॉन्फ़िगर की गई सूची से आता है, क्या `主送机关` भरा है, क्या `标题` कॉन्फ़िगर की गई लंबाई के भीतर है, क्या रजिस्टर में कोई `发文字号` दोहराया गया है, और क्या किसी शीर्षक में टेम्पलेट प्लेसहोल्डर शेष है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| दस्तावेज़ क्रमांक `某政发[2026]15号` लिखा गया, यानी वर्ग कोष्ठक के साथ। | `GW-001` उस पंक्ति को दर्ज करता है: जिस पैटर्न के साथ यह कॉन्फ़िगर हुआ है वह वर्ष के चारों ओर षट्कोणीय कोष्ठक 〔〕 माँगता है, इसलिए लिखने का रूप `某政发〔2026〕15号` है। यह नियम केवल क्रमांक का रूप देखता है — 机关代字 आपकी इकाई तय करती है, इसलिए यह नहीं आँकता कि वह सही है या नहीं, और न ही यह कि क्रमांक लगातार हैं या दोहराए गए हैं। |
| हस्ताक्षर दिनांक दस्तावेज़ की परंपरा के अनुसार लिखी है: 二〇二六年三月十五日। | `GW-002` बताता है कि यह मान पढ़ा नहीं जा सकता। यह `2026-03-15` और `2026-03-15 09:30` पढ़ता है; चीनी अंकों में लिखी दिनांक को इन दो रूपों में बदलना होगा, या यह नियम बंद करना होगा। यह नियम हस्ताक्षर दिनांक की तुलना जारी दिनांक से भी नहीं करता — वह जारी करने की प्रक्रिया का आंतरिक मामला है। |
| हमने अपनी इकाई के लिए 文种 की सूची कभी कॉन्फ़िगर नहीं की। क्या `GW-003` चुपचाप पास हो जाता है? | नहीं। `GW-003` में कोई अंतर्निहित सूची नहीं है, इसलिए `values` खाली रहने पर वह चुपचाप पास होने के बजाय रिपोर्ट के `skipped` में आता है। 《党政机关公文处理工作条例》 पंद्रह मुख्य प्रकार गिनाता है, पर यह पैक उन्हें कोड में तय नहीं करता — आपकी इकाई कौन-कौन से प्रकार इस्तेमाल कर सकती है, यह आपका निर्णय है। यह नियम यह भी नहीं आँकता कि किसी दस्तावेज़ के लिए कौन-सा प्रकार होना चाहिए था। |
| एक पंक्ति में 主送机关 खाली छोड़ा गया है। | `GW-004` उस पंक्ति को दर्ज करता है, क्योंकि मुख्य प्राप्तकर्ता के बिना यह पुष्टि नहीं होती कि दस्तावेज़ किसे भेजा गया। यह देखता है कि स्तंभ भरा है या नहीं, यह नहीं कि प्राप्तकर्ताओं का दायरा उपयुक्त है — किसे संबोधित करना और किसे प्रतिलिपि भेजनी है, यह प्रारूपण का निर्णय है। |
| हमारा शीर्षक लंबा है। यह लंबाई-सीमा कहाँ से आती है? | `GW-005` कॉन्फ़िगर की गई 60 अक्षरों की सीमा से अधिक `标题` को दर्ज करता है। यह संख्या इस नियम-पैक का डिफ़ॉल्ट मान है, किसी मानक का अंक नहीं: GB/T 9704-2012 शीर्षक के लिए केवल 「2 号小标宋体字」 तय करता है और कोई अक्षर-सीमा नहीं देता, इसलिए यदि आपकी इकाई लंबे शीर्षक लिखती है तो `maxLength` बढ़ाएँ या यह नियम बंद करें। यह नियम केवल अक्षर गिनता है — शीर्षक के शब्दों की उपयुक्तता नहीं आँकता। |
| दो पंक्तियों में एक ही 发文字号 दर्ज है। | `GW-006` दोहराए गए क्रमांक को दर्ज करता है; यह रिक्त स्थान छोड़कर मानों की तुलना करता है, और ऐसा मिलना आम तौर पर दोबारा इस्तेमाल या गलत नकल का संकेत है जिसे मनुष्य को पुष्ट करना होता है। यह तय नहीं करता कि उन दोनों में से कौन-सा दस्तावेज़ वह क्रमांक रखे। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《党政机关公文格式》 | GB/T 9704-2012（现行，本次未取得条文） | GW-001, GW-002, GW-004, GW-005, GW-007 |
| 《党政机关公文处理工作条例》 | 中办发〔2012〕14号（自 2012 年 7 月 1 日起施行） | GW-003, GW-006 |

**Boundary:** this plugin checks a **公文台账的版头与主体要素** for what a register can be held to
mechanically — that the document number follows its 「机关代字〔年份〕序号」 shape, that the signing date
parses, that the document kind comes from your vocabulary, that a main recipient is recorded, that the
title is not over-long, that numbers do not repeat, and that no template placeholder survives. It checks
**the text a register records, not the layout** — typeface, size, margins and seal placement can only be
judged from the document itself.

> ### ⚠️ What the citations in this plugin's report actually rest on
>
> **《党政机关公文处理工作条例》(中办发〔2012〕14号) was obtained and read verbatim**, and
> `rules/evidence/clause-verification.md` records which articles were quoted — article 8 (the fifteen document
> kinds), article 9 (the format elements, including 「发文字号。由发文机关代字、年份、发文顺序号组成」 and
> 「主送机关。公文的主要受理机关」), article 10 (which delegates layout to GB/T 9704-2012) and article 42
> (in force from 2012-07-01, superseding two earlier documents this pack therefore never cites).
>
> **GB/T 9704-2012 itself was not obtained.** That matters for one detail worth stating plainly: **the
> 六角括号〔〕 in `GW-001`'s pattern is the layout standard's convention, not something the regulation
> fixes** — article 9(5) requires only 「发文机关代字、年份、发文顺序号」.
>
> **The rule `excerpt` fields still say "本次未取得", and every rule remains `warn` or `info`.** What this
> plugin checks is what a *register of text* says; the regulation governs the *document*, so calling a blank
> column a `direct` breach of "a document shall consist of …" would overstate the finding. Half the rules rest
> on the layout standard or on your own convention in any case.
>
> Two thresholds are local, and the pack says so. The title-length ceiling (`GW-005`, 60 characters) is
> **this rule pack's default, not a standard figure** — article 9(7) fixes only that the title consists of the
> issuing body, the subject and the kind, and **no character count appears in either document**. And the
> document-kind vocabulary (`GW-003`) ships **empty** despite article 8 listing fifteen kinds, because the
> article says "主要有" and units also use names outside the list.
>
> The placeholder check deliberately **omits 「某」** from its term list: template titles often read
> "关于某某工作的通知", but 某 also appears in legitimate titles as a stand-in for a confidential subject.

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-gongwen-word-check
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/gongwen-word-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-gongwen-word-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-gongwen-word-check contributors.
