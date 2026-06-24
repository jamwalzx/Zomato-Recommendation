---
name: CraveAI Aura
colors:
  surface: '#131314'
  surface-dim: '#131314'
  surface-bright: '#3a393a'
  surface-container-lowest: '#0e0e0f'
  surface-container-low: '#1c1b1c'
  surface-container: '#201f20'
  surface-container-high: '#2a2a2b'
  surface-container-highest: '#353436'
  on-surface: '#e5e2e3'
  on-surface-variant: '#e5bdb6'
  inverse-surface: '#e5e2e3'
  inverse-on-surface: '#313031'
  outline: '#ac8881'
  outline-variant: '#5c403a'
  surface-tint: '#ffb4a5'
  primary: '#ffb4a5'
  on-primary: '#650b00'
  primary-container: '#ff5637'
  on-primary-container: '#590800'
  inverse-primary: '#ba1c00'
  secondary: '#e3b5ff'
  on-secondary: '#4e0079'
  secondary-container: '#6a1c9b'
  on-secondary-container: '#d99dff'
  tertiary: '#00dbe7'
  on-tertiary: '#00363a'
  tertiary-container: '#00a0a9'
  on-tertiary-container: '#002f32'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad3'
  primary-fixed-dim: '#ffb4a5'
  on-primary-fixed: '#3e0400'
  on-primary-fixed-variant: '#8e1300'
  secondary-fixed: '#f4daff'
  secondary-fixed-dim: '#e3b5ff'
  on-secondary-fixed: '#2f004c'
  on-secondary-fixed-variant: '#6a1c9b'
  tertiary-fixed: '#74f5ff'
  tertiary-fixed-dim: '#00dbe7'
  on-tertiary-fixed: '#002022'
  on-tertiary-fixed-variant: '#004f54'
  background: '#131314'
  on-background: '#e5e2e3'
  surface-variant: '#353436'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 42px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-base:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-margin: 20px
  gutter: 16px
  section-gap: 40px
  element-gap: 12px
---

## Brand & Style

The design system is centered on a high-end, futuristic "Aura" aesthetic. It targets food enthusiasts who seek an intelligent, curated, and visually stunning discovery experience. The personality is sophisticated yet energetic, moving away from the utilitarian feel of traditional food apps toward a cinematic, immersive interface.

The style leverages **Glassmorphism** and **High-Contrast Bold** elements. It utilizes deep, dark backgrounds to allow food photography to pop, paired with vibrant, glowing accents that signify AI intelligence. Transitions should feel fluid and organic, evoking a sense of "premium magic" every time the AI generates a recommendation.

## Colors

This design system uses a strict dark-mode-first approach. The foundation is a deep charcoal (#0A0A0B), which acts as the "void" where content floats. 

- **Primary Gradient:** A vibrant transition from Coral (#FF4B2B) to Deep Purple (#833AB4), used for high-action items and "AI-powered" moments.
- **Accents:** A cyan-blue (#00F2FF) is used sparingly for data-heavy elements like ratings or metallic badge reflections to add a "tech" layer.
- **Surfaces:** Instead of solid grays, surfaces use translucent white with heavy backdrop blurs (20px+) to create depth without losing the background's richness.

## Typography

Outfit is the sole typeface for this design system, chosen for its geometric precision and modern, approachable roundness. 

- **Display Text:** Use `display-lg` for AI "WOW" moments or hero restaurant titles. These should often be paired with the primary gradient.
- **Hierarchy:** Maintain high contrast between headlines (Semi-Bold/Bold) and body text (Regular).
- **Legibility:** In the dark interface, ensure `body-base` maintains a minimum opacity of 85% white to prevent eye strain while preserving the sleek aesthetic.

## Layout & Spacing

The layout follows a **fluid grid** model with generous safe areas to emphasize the premium feel. 

- **Mobile:** A 4-column grid with 20px outside margins. 
- **Desktop:** A 12-column grid centered at 1200px max-width.
- **Rhythm:** Use an 8px base unit. Section spacing should be aggressive (40px+) to allow the glassmorphic cards "room to breathe" and prevent the interface from feeling cluttered or "cheap."

## Elevation & Depth

Depth is not communicated through traditional drop shadows, but through **Tonal Layers** and **Backdrop Blurs**.

1.  **Level 0 (Base):** #0A0A0B flat background.
2.  **Level 1 (Cards):** Glassmorphic surface (5% white fill) with a 24px backdrop blur and a 1px thin border (12% white).
3.  **Level 2 (Modals/Popups):** 10% white fill with a 40px backdrop blur and a subtle outer glow using the primary gradient at 10% opacity.

**Glows:** For interactive elements, use "Ambient Glows" (diffused, low-opacity colored shadows) that match the primary gradient to simulate light emitting from the UI.

## Shapes

The shape language is consistently **Rounded**. 

- **Standard Cards/Buttons:** 16px (1rem) corner radius to feel friendly yet modern.
- **Special Elements:** Use "Pill-shaped" (full radius) for badges and tags (e.g., cuisine types).
- **Nested Elements:** Ensure inner elements have a 4px smaller radius than their containers to maintain visual harmony (e.g., a 12px image inside a 16px card).

## Components

### Buttons
- **Primary AI Button:** Uses the Coral-to-Purple gradient. It features a subtle "inner glow" and a pulse animation when the AI is processing.
- **Secondary Button:** A "Ghost Glass" style—transparent background with a 1px white border and backdrop blur.

### Glassmorphic Cards
Restaurant cards must feature high-resolution imagery with a bottom-scrim (dark gradient) to ensure typography remains readable. The card container itself uses the Level 1 elevation specs defined in Elevation & Depth.

### Segmented Controls (Budget)
A pill-shaped container with a sliding glass "indicator" that moves behind the text. Use a 1px gradient border to highlight the active state.

### Metallic Badges (Rankings)
For "Top 10" or "Crave Choice" awards, use a metallic gradient effect (Silver/Chrome) with high specularity. The badge should have a sharp, 1px "highlight" edge to simulate a physical metal texture.

### Custom Sliders (Ratings)
The slider track is a thin, dark line, while the handle is a glowing gradient orb. As the slider increases, the track fills with the primary gradient.

### Input Fields
Dark backgrounds (#000000) with a 1px glass border. On focus, the border transitions to the primary gradient with a subtle outer glow.