# Platform archetypes

Pick the closest one in Phase 0.4. It supplies what counts as first value, where the wall
usually sits, the probes that decide the run, and the scorecard rows to add. Mixed
products are common — a dev tool with a dashboard, a marketplace with a SaaS side. Take
the archetype of the path the persona would actually walk, and note the mix in the
dossier.

---

## 1. Developer tool / API

- **Arrives from:** a search for the problem, a competitor comparison, an HN or Discord
  mention, a colleague's link.
- **First value:** a successful call with their own payload, in their own terminal.
- **Usual wall:** account required for a key, or a card required past a free quota.
- **Decisive probes:**
  - Run the headline install or quickstart command exactly as written. Marketing copy
    drifts ahead of what ships; a 404 or a broken snippet on the first instruction is the
    highest-impact finding available.
  - Copy every snippet on the quickstart page and run it unedited. Count the edits needed
    to make it work — each one is a drop-off.
  - Send a realistic payload from the persona's own domain, not the docs' toy example.
  - Send the adversarial pair: an input that should trigger and a benign one that
    shouldn't. The false-positive side is where real prospects live or die.
  - Read the response envelope: which tier or model produced this, what the defaults are,
    what's missing. Say which layer produced a verdict before generalizing from it.
  - Check the error path — a bad key, a malformed body. Good errors sell; opaque 500s
    end evaluations.
  - Machine surfaces: `/openapi.json`, `/llms.txt`, SDK package pages, `/mcp`.
- **Value elements that usually decide it:** reduced anxiety about shipping it, decreased hassles at integration, legibility of what it did, and reversibility. Rarely the headline benchmark.
- **Scorecard extras:** quickstart accuracy, error message quality, SDK and language
  coverage, latency against the claim.

## 2. B2B SaaS, self-serve

- **Arrives from:** search, a review site, a peer recommendation.
- **First value:** one real task finished in the product with their own data.
- **Usual wall:** signup, then an empty state with no data to work on.
- **Decisive probes:**
  - Count the steps from landing to that first finished task, and the fields demanded
    before any value is shown.
  - The empty state: does it seed sample data, or hand the persona a blank page?
  - Import or integrate the way they actually would — CSV, Google Workspace, Slack, an
    API key from another vendor.
  - Invite a teammate: seat pricing and permissions surprises usually surface here.
  - Try to leave: is there an export? Cancellation buried?
- **Value elements that usually decide it:** time savings, reduced effort, simplification, and reputational assurance for whoever championed it internally.
- **Scorecard extras:** onboarding friction, empty-state quality, integration coverage,
  admin and permissions clarity.

## 3. Sales-led enterprise

- **Arrives from:** an analyst list, a peer, an RFP.
- **First value:** enough proof to justify booking the call.
- **Usual wall:** the demo form — often the only door.
- **Decisive probes:**
  - Can the persona build a business case without talking to anyone? Pricing anywhere?
  - The form itself: fields demanded, whether personal email is rejected, what's promised
    in return, and how fast.
  - Proof depth: named customers, real numbers, case studies with figures versus logos.
  - The compliance and security page — the thing procurement will ask for on day one.
  - Sit with the asymmetry: they're asked for contact details before being told the
    price. Is what they've been shown worth it?
- **Value elements that usually decide it:** risk reduction, regulatory compliance, stability, expertise, and blame transfer — the buyer's own exposure is the product.
- **Scorecard extras:** case-study credibility, security and compliance readiness,
  pricing transparency, form friction. **Do not submit the form** unless the operator
  approves it with a real identity (ground rule 6).

## 4. Consumer app / subscription

- **Arrives from:** an ad, an app store listing, social, a friend.
- **First value:** the first moment of enjoyment or relief, usually inside two minutes.
- **Usual wall:** signup before anything, or a paywall right after the first taste.
- **Decisive probes:**
  - Mobile viewport first — this persona is on a phone. Screenshot there.
  - Time to the first pleasant moment. Anything before it that isn't earning its place is
    a leak.
  - The paywall: does it arrive before or after value? Is the trial's terms clear, and is
    cancellation findable?
  - Check for dark patterns explicitly: pre-checked boxes, hidden renewal, confirmshaming,
    a cancel flow longer than the signup.
  - Store reviews as an outside view on what breaks in week two.
- **Value elements that usually decide it:** reduced anxiety, therapeutic value, fun, badge value, and reversibility at the paywall. Use the B2C ladder.
- **Scorecard extras:** time-to-delight, paywall fairness, cancellation honesty, mobile
  polish.

## 5. Marketplace

- **Arrives from:** search, usually with intent already formed.
- **First value:** finding a listing they'd actually pick.
- **Usual wall:** account required to see prices, contact a seller, or check out.
- **Decisive probes:**
  - Walk both sides — the buyer's path and the supply side's path. Thinness on either
    side is the whole business.
  - Search with a real query, then filter. Do results survive contact with specifics?
  - Inventory depth in the persona's niche and location, not the homepage's showcase.
  - Trust machinery: reviews, verification, dispute and refund terms, who holds the money.
  - Total cost at checkout versus the listed price — where the fees appear.
- **Value elements that usually decide it:** variety, availability, and trust in strangers — liquidity in the persona's own niche beats every feature. B2C ladder.
- **Scorecard extras:** liquidity in the persona's niche, search and filter quality, trust
  and safety, fee transparency.

## 6. Ecommerce / DTC

- **Arrives from:** an ad, search, social.
- **First value:** confidence this specific product is right for them.
- **Usual wall:** none until checkout — the wall is doubt, not auth.
- **Decisive probes:**
  - Product page: does it answer sizing, materials, and "will this work for me"?
  - Shipping cost and delivery date — how deep into checkout before they're revealed?
  - Returns policy findability, and how it reads.
  - Add to cart and go as far as the payment step without paying. Count the steps, note
    forced account creation, watch for surprise fees.
  - Reviews: real, filtered, or absent?
- **Value elements that usually decide it:** sensory appeal, avoids hassles, quality, and reversibility (returns). B2C ladder.
- **Scorecard extras:** product-page completeness, shipping and returns clarity, checkout
  friction, review credibility.

## 7. Content, media, or community

- **Arrives from:** a single link — an article, a post, a video.
- **First value:** one piece of content worth their time.
- **Usual wall:** a meter, a registration wall, or a newsletter interstitial.
- **Decisive probes:**
  - Read the landing article as a reader: ads, interstitials, layout shift, how long until
    the actual text.
  - Is there a second thing worth reading? Recirculation is the whole model.
  - The subscribe ask: when it fires, what it offers, what it costs.
  - For a community: how alive is it, and how visible is that from outside? Last post
    date, unanswered threads, who replies.
- **Value elements that usually decide it:** informs, affiliation and belonging, therapeutic value, and design. B2C ladder.
- **Scorecard extras:** reading experience, ad load, recirculation, community liveness.

## 8. Open source project

- **Arrives from:** GitHub, a package registry, a blog post.
- **First value:** it running locally against their own case.
- **Usual wall:** none technically — the wall is maintenance risk and setup cost.
- **Decisive probes:**
  - README as a stranger: install, run the example, count the undocumented steps.
  - Health signals: last commit, open issue age, unanswered issues, release cadence,
    number of maintainers, licence.
  - Docs beyond the README — the page their real integration needs.
  - The commercial edge: is there a hosted version, and what's held back from the OSS one?
- **Value elements that usually decide it:** cost reduction, flexibility, component quality, marketability of the skill, and blame transfer — which nobody gets, and that's the whole objection.
- **Scorecard extras:** setup cost, project health, docs beyond README, licence fit.

---

## When the archetype is unclear

Ask what a stranger would try to do in their first five minutes and follow that. If two
archetypes fit equally, run the spine on the persona's likely path and note in the report
that the other path exists and wasn't walked.
