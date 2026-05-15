# Assessment Brief — Frontend Engineer (Data Dashboard)

## Role Description
Mid-level frontend engineer. 2–4 years experience. Has built at least one data-heavy UI — tables, charts, filters. Comfortable with the DOM, vanilla JS, and reading a dataset.

## Business Context

RetailPulse is an e-commerce analytics startup. Their ops team uses a sales dashboard every morning to review the previous day's performance. The current dashboard is a static HTML mockup — all the DOM nodes are in place, the sample dataset is loaded, but nothing actually works yet. A candidate must wire up the logic entirely in `script.js` without touching `index.html` or `data.js`.

## Schema / Requirements

The `window.ORDERS` array is injected by `data.js`. Each order object has the following shape:

| Field | Type | Example |
|-------|------|---------|
| id | string | "ORD-001" |
| customer | string | "Alice Martin" |
| date | string (YYYY-MM-DD) | "2024-01-05" |
| amount | number | 120.00 |
| status | string | "completed" \| "refunded" \| "pending" |

## Functional Requirements

1. On page load, populate the three summary cards using **all orders** in `window.ORDERS`:
   - `#total-revenue` — sum of `amount` for `status === "completed"` orders, formatted as `$X,XXX.XX`.
   - `#total-orders` — count of all orders regardless of status.
   - `#avg-order` — average `amount` across completed orders only, formatted as `$X,XXX.XX`.
2. Render a **bar chart** on `#revenue-chart` (using the native Canvas 2D API — no Chart.js or other libraries) showing monthly completed revenue for the visible date range. X-axis = month label (e.g. "Jan 2024"), Y-axis = revenue.
3. Populate `#orders-body` with one `<tr>` per order matching the current filter, with columns in the order: Order ID, Customer, Date, Amount, Status.
4. The **Apply** button (`#apply-filter`) must re-filter `window.ORDERS` using `#date-from` and `#date-to` values and re-render cards, chart, and table.
5. If no date range is set, show all orders.
6. Orders with `status === "refunded"` must render with a CSS class `row-refunded` on their `<tr>`.
7. No external libraries. Vanilla JS and Canvas 2D API only.

Starter code: https://gist.github.com/ngm9/d360e001ccb6bc5cbc0ed901ce41b618

## Evaluation Criteria

- Summary cards populated correctly from `window.ORDERS` on load
- Bar chart rendered with Canvas 2D API — correct monthly grouping and labelling
- Table rows populated with correct data and column order
- Date filter correctly re-renders all three sections
- `row-refunded` class applied to refunded order rows
- No modifications to `index.html` or `data.js`
- No external libraries used
