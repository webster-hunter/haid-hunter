# Style Guide — Slate Blue Web App

## Colors

| Token               | Hex       | Usage                          |
|---------------------|-----------|--------------------------------|
| `--color-bg`        | `#0D1117` | Page background                |
| `--color-surface`   | `#161B2E` | Cards, modals                  |
| `--color-elevated`  | `#1E2A45` | Dropdowns, sidebars            |
| `--color-border`    | `#2E3F5C` | Dividers, input borders        |
| `--color-muted`     | `#6B7FA3` | Captions, placeholders         |
| `--color-text`      | `#C8D3E8` | Body text                      |
| `--color-primary`   | `#4A6FA5` | Buttons, links, active states  |
| `--color-secondary` | `#7B93D4` | Badges, tags, hover accents    |
| `--color-accent`    | `#F59E0B` | CTAs, highlights, alerts       |
| `--color-success`   | `#10B981` | Confirmations                  |
| `--color-error`     | `#EF4444` | Errors, destructive actions    |

---

## Typography

| Role        | Font            | Size | Weight |
|-------------|-----------------|------|--------|
| Display     | Inter           | 48px | 700    |
| H1          | Inter           | 32px | 700    |
| H2          | Inter           | 24px | 600    |
| H3          | Inter           | 18px | 600    |
| Body        | Inter           | 16px | 400    |
| Small       | Inter           | 14px | 400    |
| Label       | Inter           | 12px | 500    |
| Mono/Code   | JetBrains Mono  | 14px | 400    |

Line height: `1.6` body, `1.2` headings. Letter spacing: `0.01em` body, `0.05em` labels (uppercase).

---

## Spacing (4px base unit)

| Token  | Value |
|--------|-------|
| `xs`   | 4px   |
| `sm`   | 8px   |
| `md`   | 16px  |
| `lg`   | 24px  |
| `xl`   | 32px  |
| `2xl`  | 48px  |
| `3xl`  | 64px  |

---

## Border Radius

| Token  | Value  | Usage                  |
|--------|--------|------------------------|
| `sm`   | 4px    | Inputs, badges         |
| `md`   | 8px    | Cards, buttons         |
| `lg`   | 12px   | Modals, panels         |
| `full` | 9999px | Pills, avatars         |

---

## Shadows

| Token  | Value                                              |
|--------|----------------------------------------------------|
| `sm`   | `0 1px 3px rgba(0,0,0,0.4)`                       |
| `md`   | `0 4px 12px rgba(0,0,0,0.5)`                      |
| `lg`   | `0 8px 24px rgba(0,0,0,0.6)`                      |
| `glow` | `0 0 16px rgba(74,111,165,0.4)`                   |

---

## Components

**Buttons**
- Primary: `--color-primary` bg, white text, `md` radius, `sm`–`md` padding
- Secondary: transparent bg, `--color-border` border, `--color-text` text
- Destructive: `--color-error` bg on hover/confirm only
- Disabled: 40% opacity, no pointer events

**Inputs**
- Background: `--color-elevated`
- Border: `--color-border`, focus → `--color-primary`
- Radius: `sm`
- Placeholder: `--color-muted`

**Cards**
- Background: `--color-surface`
- Border: `1px solid --color-border`
- Radius: `lg`
- Shadow: `md`

---

## Motion

| Token    | Value                                      | Usage            |
|----------|--------------------------------------------|------------------|
| `fast`   | `100ms ease`                               | Hover states     |
| `base`   | `200ms ease`                               | Buttons, inputs  |
| `slow`   | `300ms ease-in-out`                        | Modals, panels   |
| `spring` | `400ms cubic-bezier(0.34, 1.56, 0.64, 1)` | Dropdowns        |

---

## Iconography

- Library: **Lucide Icons**
- Default size: `20px`
- Stroke width: `1.5`
- Color: inherits from text context
