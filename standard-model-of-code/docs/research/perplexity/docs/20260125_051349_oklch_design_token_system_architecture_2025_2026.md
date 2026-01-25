# Research: OKLCH design token system architecture 2025-2026: Best practices for integrating OKLCH color space i...

> **Date:** 2026-01-25 05:13:49
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:9c449c0c20bcfa904fab23bdf6ee2ad20aacd23e7d075887e3a7aa02c0ebf252`
> **Raw JSON:** `raw/20260125_051349_oklch_design_token_system_architecture_2025_2026.json`

---

## Query

OKLCH design token system architecture 2025-2026: Best practices for integrating OKLCH color space into a design token system. Specifically:

1. How should OKLCH values (L, C, H) map to semantic design tokens (primary, secondary, accent, surface, etc.)?
2. What is the recommended structure for OKLCH-based design token files (JSON/YAML)?
3. How do modern design systems handle gamut mapping and fallbacks for OKLCH colors?
4. What are the accessibility considerations for OKLCH-based color tokens (contrast ratios, perceptual uniformity)?
5. How do Figma Tokens, Style Dictionary, and other tools handle OKLCH in 2025-2026?

Provide concrete examples and schema structures.

---

## Response

# OKLCH Design Token System Architecture: Best Practices and Implementation for 2025-2026

The emergence of OKLCH as a standardized color space represents a fundamental shift in how design systems approach color management and accessibility. With browser adoption now exceeding ninety-three percent and the Design Tokens Community Group achieving its first stable specification in 2025[56], organizations are increasingly moving beyond legacy RGB and HSL color models to implement perceptually uniform color systems that offer superior control, consistency, and accessibility properties. This comprehensive report examines the architectural principles, technical implementation strategies, and practical methodologies for integrating OKLCH color spaces into modern design token systems, providing guidance for design systems teams, tool makers, and development organizations seeking to establish future-proof color management infrastructure.

## Understanding OKLCH as a Perceptually Uniform Color Foundation

Before examining the architectural implications of OKLCH adoption, it is essential to understand the fundamental properties that distinguish OKLCH from traditional color models and why these properties have profound consequences for design token architecture. OKLCH, which stands for Oklab Lightness, Chroma, and Hue, is a cylindrical representation of the OKLAB color space, which was specifically designed to correct the shortcomings of earlier perceptually uniform color models such as CIELAB[1][4]. The three components of OKLCH operate on distinct perceptual dimensions: lightness (L) ranges from zero to one (or zero to one hundred percent), representing perceived brightness on a scale that closely mirrors human vision; chroma (C) represents the colorfulness or saturation of the color, ranging theoretically from zero to infinity but practically remaining below 0.5 in most implementations; and hue (H) represents the angle of the color on the color wheel, measured in degrees from zero to three hundred sixty[1][4][18].

The perceptual uniformity of OKLCH means that equal numerical changes in any of its components produce equal perceived visual differences, a property that is mathematically absent in traditional RGB and HSL color spaces[4][7][21]. This characteristic has immediate and cascading implications for how design tokens should be structured. In RGB color spaces, for example, a change from RGB(100, 100, 100) to RGB(150, 100, 100) produces a different perceptual change than moving from RGB(200, 150, 150) by the same absolute amount, and the perceptual change varies depending on which component is being modified. Conversely, in OKLCH, adjusting lightness by 0.1 produces a visually consistent change regardless of whether the color is a vibrant blue or a muted green[21][22]. This property enables design systems to create color scales with natural-feeling transitions and maintain consistent accessibility ratios across different hue families without manual adjustment for each color[2][49].

The wider color gamut support of OKLCH represents another critical architectural consideration. OKLCH can encode colors in the Display P3 color space, which contains approximately thirty percent more colors than the traditional sRGB gamut[4][7]. For design systems targeting modern devices with wide-gamut displays—particularly smartphones and professional monitors—this expanded palette offers opportunities for richer, more vibrant color expression while maintaining accessibility and brand fidelity[21]. However, this capability introduces the technical complexity of managing fallbacks for devices limited to sRGB color space, a challenge that fundamentally shapes how token files should be structured and how build systems must process color definitions[9][17].

## Mapping OKLCH Components to Semantic Design Token Hierarchies

The transformation from OKLCH's technical color space into a usable semantic token system requires a carefully considered hierarchical structure that bridges the gap between perceptually uniform color mathematics and meaningful design intent. Design systems traditionally employ multiple token levels, beginning with base or primitive tokens that represent fundamental design decisions, advancing through component-specific tokens that apply to particular UI elements, and culminating in semantic tokens that encode meaning and usage guidance[25][39][42]. When OKLCH is introduced into this hierarchy, each level takes on specific responsibilities and constraints.

At the primitive or base token level, OKLCH colors should be organized into atomic color palettes grouped by hue family, with each hue family containing a consistent set of lightness levels[2][13][49]. The recommended approach involves creating approximately ten to thirteen discrete lightness values for each hue, arranged in increments that ensure perceptual uniformity while providing adequate coverage for different use cases[13][49]. For a primary brand color, for instance, you might define tones numbered fifty, one hundred, two hundred through nine hundred in increments of one hundred, following a pattern where the numbering convention allows for future insertion of intermediate values without disrupting the existing token naming structure[1][10][18][25]. Each token at this level should maintain a constant hue and vary primarily in lightness, with chroma adjustments reserved for refinement based on visual evaluation[2][13].

Within the atomic palette layer, the relationship between lightness values and practical application becomes crucial. Colors at the extreme ends of the lightness scale (very light tones in the range of ninety to ninety-eight percent lightness, and very dark tones below ten percent lightness) are typically reserved for backgrounds or minimal-contrast applications, while tones in the middle ranges—particularly those with lightness values between forty and sixty percent—carry maximum chroma and serve as accent colors[2][13][49]. This distribution ensures that when colors are applied to create backgrounds and foreground elements, the perceptual uniformity of OKLCH automatically maintains consistent contrast ratios across different hue families. For example, if a specific lightness value like fifty percent provides adequate contrast when used as text on a white background, the same fifty percent lightness value applied to a different hue should provide visually similar contrast characteristics[2][26][49].

The semantic layer builds directly upon these atomic primitives by creating named tokens that encode usage intent rather than merely describing color properties. Where primitive tokens might be named `color.blue.500` or `color.teal.600`, semantic tokens adopt names like `color.background.primary`, `color.text.secondary`, `color.border.emphasis`, or `color.surface.interactive`[13][25][42]. These semantic tokens typically reference primitive tokens through token aliasing mechanisms, allowing designers and developers to discuss color choices using meaningful language while maintaining a clear provenance back to the underlying color mathematics. A semantic token for button background color might be defined as a reference to `color.blue.600`, but this semantic layer provides the important contextual information that this particular shade of blue is specifically chosen for button backgrounds[2][13][49].

The challenge in mapping OKLCH components to semantic tokens becomes particularly complex when designing for multiple themes, interaction states, and accessibility requirements. A comprehensive semantic token system should define variants for different contexts: primary states for default appearance, hover states that typically involve a lightness adjustment of approximately 0.1 (ten percent), active or pressed states with similar lightness modifications, and disabled states that often employ reduced chroma or neutral hues[2][13][49]. The perceptual uniformity of OKLCH makes this remarkably tractable because the same lightness adjustment produces visually consistent results across all hue families. A button background might move from `oklch(56% 0.25 260)` in its default state to `oklch(46% 0.25 260)` in its hover state, applying a uniform lightness reduction while preserving hue and chroma[2][22][49].

For surface and background colors, the semantic mapping should recognize the distinction between primary surfaces (large-area backgrounds that establish the overall tone), secondary surfaces (intermediate background layers), and interactive surfaces (small focused areas like buttons or form inputs)[2][13][49]. A light mode theme might define `color.surface.primary` as a near-white color with lightness values exceeding ninety-five percent and minimal chroma, while `color.surface.interactive` might employ a more neutral tone with slightly higher chroma for visual interest. Dark mode variants would reverse this logic, beginning from very dark tones and scaling upward[2][13][49]. By using OKLCH's perceptual uniformity, the same semantic token names can serve both light and dark themes through simple value references, avoiding token proliferation and maintaining consistency[2][26].

Accent and emphasis colors require specialized mapping approaches. Primary brand colors often pose particular challenges because they may need to serve simultaneously as background colors, text colors, and border colors in different contexts[13][49]. Rather than forcing a single primary color to perform all these functions, sophisticated token systems create multiple variants: `color.brand.primary` for the most vibrant, visually prominent application (often at high chroma and moderate lightness); `color.brand.secondary` for applications requiring somewhat reduced intensity; and `color.text.brand` for situations where the primary brand color is too light or insufficiently contrasted for readable text[13][49]. These variants typically employ the same base hue but vary lightness and chroma independently, leveraging OKLCH's ability to manipulate these dimensions without affecting hue perception.

## Design Token File Architecture and JSON/YAML Structure

The practical representation of OKLCH design tokens within file systems requires careful attention to both the technical requirements of various tools and the cognitive ergonomics of maintaining these files. The Design Tokens Community Group's specification, which achieved stability in version 2025.10, provides normative guidance on token file structure while also defining extension points where implementations can incorporate additional features[1][3][56]. Understanding both the standard specification and the practical extensions employed by leading design systems provides the foundation for effective token architecture.

At the fundamental level, design token files following the DTCG specification employ either JSON or YAML formats, with JSON historically being the standard while YAML gains adoption for its improved readability and reduced syntactic overhead[3][39][56]. Each token requires at minimum a `$type` property and a `$value` property, with optional `$description` properties providing crucial documentation of intended usage[3][39]. For OKLCH colors specifically, the value can be expressed as either a simple string following CSS color notation or as a structured object that explicitly specifies color space, components, and fallback values[1][3][10][55].

The simplest OKLCH token representation employs direct CSS notation:

```yaml
color:
  blue:
    500:
      $type: color
      $value: oklch(56% 0.15 260)
      $description: Primary blue for interactive elements
```

This string-based format offers excellent compatibility with modern tools and provides human-readable color values that developers can understand at a glance. However, for systems requiring explicit gamut mapping, fallback support, or complex color space specifications, the object-based format provides necessary control:

```yaml
color:
  blue:
    500:
      $type: color
      $value:
        colorSpace: oklch
        components: [0.56, 0.15, 260]
        alpha: 1
      $description: Primary blue for interactive elements
```

When implementing fallback values for devices lacking Display P3 support, the token structure expands further to accommodate multiple representations:

```yaml
color:
  blue:
    500:
      $type: color
      $value:
        colorSpace: oklch
        components: [0.56, 0.15, 260]
        alpha: 1
        hex: "#0077CC"
      $description: Primary blue, with sRGB fallback
```

For design systems managing multiple themes, interaction states, and accessibility variants, the token structure must accommodate conditional values triggered by media queries or theme contexts. The Firefox design token system, which has been refined for production use across multiple platforms, demonstrates this through nested value objects:

```yaml
color:
  blue:
    primary:
      value:
        light: oklch(95% 0.02 260)
        dark: oklch(25% 0.05 260)
      description: Primary text color adapting to light and dark modes
```

This structure automatically generates separate CSS variables for light and dark theme contexts, enabling themes to coexist within the same stylesheet without manual duplication[6][12]. Similarly, systems supporting accessibility features like high-contrast mode can employ nested structures under `prefersContrast` or `forcedColors` keys[6][12].

The atomic color palette layer requires a particular structural approach that balances between maintaining flat, manageable file hierarchies and encoding the relationships between colors within a hue family. A common pattern organizes colors into groups by hue, with numeric scales indicating lightness progression:

```yaml
color:
  blue:
    50:
      $type: color
      $value: oklch(98% 0.008 250)
    100:
      $type: color
      $value: oklch(93% 0.028 250)
    200:
      $type: color
      $value: oklch(80% 0.045 250)
    300:
      $type: color
      $value: oklch(66% 0.056 250)
    400:
      $type: color
      $value: oklch(58% 0.059 250)
    500:
      $type: color
      $value: oklch(49% 0.053 250)
    600:
      $type: color
      $value: oklch(35% 0.042 250)
    700:
      $type: color
      $value: oklch(20% 0.025 250)
```

This structure ensures that hue remains constant across the scale (two hundred fifty degrees throughout the blue family) while lightness decreases predictably from fifty (98% lightness) through seven hundred (20% lightness). The chroma values in this example follow a curve that rises toward the middle values (maximum saturation in the mid-tone ranges) and diminishes at the extremes, a pattern that ensures natural, visually harmonious color progressions[13][49].

The semantic token layer typically resides in separate file groups that reference these atomic primitives through token aliasing. A practical semantic color file might be organized as follows:

```yaml
color:
  background:
    primary:
      $type: color
      $value: "{color.neutral.50}"
      $description: Primary surface for light mode
    secondary:
      $type: color
      $value: "{color.neutral.100}"
      $description: Secondary surface for card backgrounds
    interactive:
      $type: color
      $value: "{color.neutral.75}"
      $description: Background for interactive elements like buttons
  text:
    primary:
      $type: color
      $value: "{color.neutral.900}"
      $description: Primary text color for maximum contrast
    secondary:
      $type: color
      $value: "{color.neutral.700}"
      $description: Secondary text for supporting information
    brand:
      $type: color
      $value: "{color.blue.600}"
      $description: Brand-colored text for emphasis
```

For systems managing multiple token sets (light theme, dark theme, high-contrast variants), Style Dictionary and similar build tools support organizing tokens into separate files that can be selectively enabled or combined. Mozilla's Firefox design system, for instance, maintains separate token definitions for platform-specific values and brand-specific values, allowing the same semantic token names to resolve to different underlying colors depending on context[6][12].

The structure of OKLCH token files should account for the practical tooling limitations and capabilities. Figma Tokens, which serves as a widely adopted plugin for design systems, requires token sets to maintain flat or folder-based hierarchies and supports OKLCH notation directly when using modern color picker integrations[8][20][23]. Style Dictionary, an open-source tool for transforming design tokens into platform-specific formats, accepts OKLCH values in DTCG-compliant JSON structures and can apply gamut mapping transformations during the build process[6][9][12]. By structuring tokens according to the DTCG specification while remaining aware of tool-specific capabilities, design systems can maintain maximum interoperability while leveraging the strengths of different platforms.

## Gamut Mapping and Cross-Platform Fallback Strategies

One of the most technically complex aspects of implementing OKLCH in production design systems involves managing the mismatch between the wide color gamut that OKLCH can theoretically represent and the limited gamut of devices where applications will actually run. The vast majority of desktop monitors and consumer devices support only the sRGB color gamut, which contains fewer colors than the Display P3 gamut used on modern smartphones and professional displays[4][7][19]. When an OKLCH color falls outside the sRGB gamut—which is particularly common for highly saturated colors at mid-tone lightness values—the color must be converted to the closest in-gamut equivalent for fallback purposes[10][17][34].

Gamut mapping is the process of converting out-of-gamut colors to the closest representable colors within a target color space[10][17][43]. The DTCG specification acknowledges that multiple gamut mapping algorithms exist, each with different properties and appropriate use cases[10]. The most commonly implemented algorithm for OKLCH-to-sRGB conversion, the "oklch-chroma" method, reduces the chroma of the color via binary search until the color falls within the sRGB gamut while preserving both lightness and hue[10][43]. This approach maintains the perceptual quality of the color while ensuring compatibility with legacy devices, though the resulting sRGB color may be visually less vibrant than the original OKLCH specification[17].

A practical example illustrates this process. Consider an OKLCH color specified as `oklch(57% 0.24 23)`, which represents a moderately saturated red-orange. This color exists in the Display P3 gamut but not in the standard sRGB gamut. When gamut-mapped to sRGB using the chroma-reduction algorithm, it converts to approximately `#df002d`. The perceptual appearance remains similar—still recognizably red-orange, still at comparable lightness—but with slightly reduced saturation[9][17]. The contrast ratio between this mapped color and white text, measured at 5.02:1, exceeds the WCAG AA accessibility requirement of 4.5:1, confirming that the mapped color remains suitable for its intended use despite the conversion[9][17].

Design token systems should implement gamut mapping at the build-time level rather than attempting to manage it manually. The PostCSS OKLab Function plugin, for instance, automatically converts OKLCH values to sRGB fallbacks during CSS processing, optionally preserving the original OKLCH notation for browsers that support it[38]. A practical build configuration might specify:

```json
{
  "color": {
    "primary": {
      "value": "oklch(56% 0.25 260)"
    }
  }
}
```

During the build process, this specification generates CSS variables with multiple fallback layers:

```css
--color-primary: rgb(0, 119, 204);
--color-primary: color(display-p3 0.15 0.50 0.85);
--color-primary: oklch(56% 0.25 260);
```

Browsers render the last format they understand, ensuring that Display P3-capable devices render the most vibrant color while older browsers fall back gracefully[38]. This approach requires no manual management by designers and scales automatically across hundreds of color tokens[9][17][38].

The specific choice of gamut mapping algorithm should depend on the design system's priorities. The chroma-reduction approach preserves lightness and hue, making it ideal for systems where perceptual uniformity and accessible contrast ratios are paramount[34][43]. Alternative approaches, such as saturation-based reduction or relative colorimetric mapping, may be appropriate for systems with different priorities[10][34][43]. Design system architects should document which algorithm is applied and validate the results by spot-checking critical color pairs to ensure contrast ratios remain within accessibility requirements[9][17][34].

For design systems operating across multiple platforms—particularly those supporting iOS, Android, and web simultaneously—fallback strategies become even more critical. iOS and Android platforms have varying levels of OKLCH support depending on the framework and runtime version. A pragmatic approach involves specifying colors in sRGB-compatible formats as the baseline, supplemented with OKLCH specifications for platforms that support them[25][38][56]. Style Dictionary and similar tools can generate platform-specific output formats, automatically selecting appropriate color specifications for iOS Swift enums, Android XML resources, CSS custom properties, and JSON exports[9][12][25].

The challenge of maintaining consistent color appearance across platforms and devices necessitates careful testing and validation. Design systems should establish processes for evaluating how colors appear on different device types—particularly comparing sRGB fallbacks on standard monitors against Display P3 colors on wide-gamut displays. Tools like WebGL color viewers and platform-specific preview applications enable this validation[21][24][33]. Additionally, design documentation should explicitly acknowledge the visual differences between sRGB fallback colors and their OKLCH specifications, setting appropriate expectations for design and development teams[17].

## Accessibility Considerations and Contrast Management with OKLCH

The perceptual uniformity of OKLCH introduces fundamental changes to how design systems approach accessibility and color contrast, shifting from manual contrast ratio calculations based on RGB fallback colors to predictable, mathematically grounded contrast management based on lightness differences. This transformation represents one of the most significant practical benefits of OKLCH adoption, enabling design systems to scale color palettes with confidence that accessibility requirements will be met across diverse color families.

The relationship between OKLCH lightness and perceived brightness is so consistent that the W3C's WCAG 3 specifications, currently in development, have shifted to emphasizing the Advanced Perceptual Contrast Algorithm (APCA) which operates directly on perceptually uniform color spaces[34][57]. While WCAG 2 contrast ratios, which form the current accessibility baseline, technically calculate based on relative luminance derived from RGB values, applying OKLCH tokens with appropriate lightness separation achieves equivalent or superior results in practice[2][9][17][34]. The fundamental principle is straightforward: when two colors differ by a consistent lightness value in OKLCH space—say, one hundred-forty tones apart when using HCT, or thirty percent lightness separation in OKLCH—they will produce similar contrast ratios regardless of whether one is blue and the other is green[2][26][34].

A practical implementation ensures that semantic tokens for text and backgrounds maintain sufficient lightness separation. Research suggests that a lightness difference of approximately thirty to forty percent between foreground and background colors typically satisfies WCAG AA contrast requirements[2][26][34]. For example, if a background surface is defined as `color.surface.primary` with a lightness of ninety-five percent, text applied over that background should employ a lightness value around fifty-five to sixty-five percent to maintain adequate contrast. This separation, when applied consistently across all hue families, produces visually equivalent contrast levels regardless of whether the text is blue, red, or green[2][26][34].

Design systems should document the lightness ranges that correspond to specific accessibility levels. A practical guideline might establish:

- Lightness values from zero to twenty percent: reserved for dark text or very dark backgrounds
- Lightness values from twenty to forty percent: suitable for secondary text and interactive elements
- Lightness values from forty to sixty percent: appropriate for primary text and neutral backgrounds
- Lightness values from sixty to eighty percent: suitable for light backgrounds and secondary surfaces
- Lightness values from eighty to one hundred percent: reserved for very light backgrounds and minimal-contrast applications

By organizing semantic tokens according to these ranges, designers can make accessibility-conscious color choices at design time rather than requiring post-hoc contrast ratio verification[2][26][34][49].

The particular advantage of OKLCH for accessible color systems emerges when designing for dark mode variants. Rather than creating entirely separate color palettes for dark themes, designers can leverage the fact that OKLCH's perceptual uniformity makes the same semantic token names applicable to different OKLCH values in different themes[2][26]. A token defined as:

```yaml
color:
  text:
    primary:
      value:
        light: oklch(8% 0.02 260)
        dark: oklch(92% 0.02 260)
```

automatically provides appropriate contrast in both light and dark contexts because the lightness values are inverse while maintaining similar perceived saturation[2][26][49]. This pattern scales across dozens or hundreds of semantic tokens without requiring separate token definitions for dark mode.

The emerging APCA contrast algorithm provides even more precise accessibility guidance by considering font properties, text purpose, and perceptual characteristics in addition to simple color differences[34][57]. Tools implementing APCA, such as the Polychrom Figma plugin, work directly with OKLCH colors to suggest accessible color adjustments while minimizing visual changes to the design[24][60]. Rather than reducing a color's saturation indiscriminately to improve contrast, APCA-aware tools can adjust lightness alone, leveraging OKLCH's ability to modify this dimension independently. For example, a button color might shift from `oklch(56% 0.25 260)` to `oklch(42% 0.25 260)` to meet accessibility requirements while maintaining the original hue and saturation[24][34][60].

Specialized tools for accessibility-focused color optimization now employ OKLCH directly in their constraint satisfaction algorithms. A research implementation recently demonstrated that using OKLCH space with constrained optimization techniques can automatically modify colors to meet WCAG AA requirements while minimizing perceptual change, achieving acceptable results in over seventy-seven percent of accessibility violation cases with median perceptual differences below the just-noticeable-difference threshold[34]. This capability suggests that future design system tooling will increasingly automate the process of ensuring accessible color combinations through intelligent OKLCH-based manipulation.

Design systems should establish clear accessibility documentation that connects OKLCH lightness values to WCAG compliance levels. Rather than requiring designers to manually verify contrast ratios, documentation should communicate that combinations meeting the established lightness separation guidelines automatically satisfy accessibility requirements[2][9][26][34]. This shift from outcome-based verification to rule-based design dramatically reduces the cognitive load on design teams while improving overall accessibility outcomes.

## Tool Ecosystem and Implementation: Figma Tokens, Style Dictionary, and Modern Platforms

The practical adoption of OKLCH in design systems depends critically on tooling support and the ability to integrate OKLCH-based tokens seamlessly into existing design and development workflows. As of 2025-2026, a mature ecosystem of tools has emerged to support OKLCH color token management, though native support within mainstream design tools remains limited, necessitating creative use of plugins and build-time transformations.

Figma, the dominant design tool for design systems work, does not yet natively support OKLCH in its color picker interface. However, multiple third-party plugins enable OKLCH workflows within Figma. The Prism plugin generates comprehensive OKLCH palettes from a single base color, automatically creating tints and shades across all lightness values[5]. The Supa Design Tokens plugin supports OKLCH with Display P3 compatibility and includes accessibility features[8]. For design systems managing tokens through Tokens Studio, the plugin can parse OKLCH values in token files and apply them to Figma components, though visual feedback occurs through the resolved RGB representation[20][23]. This creates a practical workflow where designers work with semantic token names in Figma while the underlying OKLCH mathematics operates invisibly during the token resolution process.

The recommended Figma workflow for OKLCH-based design systems involves maintaining tokens in external JSON or YAML files synchronized with Figma through Tokens Studio or similar bridge tools. Designers reference semantic token names (like `color.background.primary` or `color.text.secondary`) when styling components, while the token resolution process maps these names to OKLCH values stored in source files. Build processes then handle the transformation from OKLCH to platform-specific formats[20][23][44]. This approach maintains Figma's visual design capabilities while leveraging OKLCH's mathematical properties for consistency and scalability.

Style Dictionary, an open-source tool maintained by Amazon and widely adopted across design systems, provides production-grade support for OKLCH-based tokens[9][12]. The tool accepts DTCG-compliant token definitions and transforms them into platform-specific outputs: CSS custom properties with sRGB and Display P3 fallbacks, iOS Swift code, Android XML resources, and JSON exports[6][9][12]. A typical Style Dictionary configuration for OKLCH colors might specify:

```javascript
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [{
        destination: 'colors.css',
        format: 'css/variables'
      }]
    },
    ios: {
      transformGroup: 'ios',
      buildPath: 'dist/ios/',
      files: [{
        destination: 'Colors.swift',
        format: 'ios/colors.swift'
      }]
    }
  }
};
```

During the build process, Style Dictionary applies platform-specific transformations, automatically handling gamut mapping for sRGB targets while preserving OKLCH values for web outputs supporting Display P3[9][12]. This approach eliminates manual color format conversion and enables teams to maintain a single source of truth that scales across web, iOS, Android, and other platforms.

Tokens Studio for Figma, which has become the de facto standard for design token management within Figma workflows, achieved significant improvements in version 3.0 and beyond by adding native OKLCH support and improved multi-file token management[20][23][44]. The plugin allows designers to define and organize tokens directly within Figma, then export them in DTCG-compliant formats for integration with build systems like Style Dictionary. The workflow typically involves:

1. Defining primitive and semantic tokens within Tokens Studio, leveraging the plugin's built-in OKLCH color picker or integrations with third-party tools
2. Exporting tokens to JSON files that follow the DTCG specification
3. Committing these files to version control alongside application code
4. Running build processes (typically within CI/CD pipelines) to transform tokens into platform-specific formats
5. Importing transformed tokens back into Figma components or applying them directly in application code

Recent versions of Tokens Studio (Pro tier) support advanced features including multi-file management, theme management, branch switching, and composition tokens that reference other tokens[20][23]. These capabilities enable sophisticated design systems to manage complex token hierarchies with multiple themes and variant layers.

Mozilla's Firefox design system provides a production implementation demonstrating OKLCH token management at scale[6][12]. The system maintains design tokens in a master JSON file that sources specifications for multiple platforms. The token structure separates platform-specific values and brand-specific values, allowing the same semantic token names to resolve to different OKLCH specifications depending on context. The Firefox build process uses Style Dictionary to transform these tokens into:

- CSS files with sRGB fallbacks and Display P3 variants for web components
- Platform-specific colors files for native UI elements
- JavaScript exports for runtime color access

This approach has been refined through years of production use and serves as a reference implementation for organizations building similar systems.

Beyond these primary tools, a mature ecosystem of supporting utilities has emerged around OKLCH color token implementation. ColorAide, a comprehensive color mathematics library supporting all CSS Color Module Level 4 color spaces, enables sophisticated color manipulation and gamut mapping[43]. The `oklch.com` color picker, maintained by Evil Martians, provides both educational resources and practical tools for working with OKLCH colors[24][33][46]. The Harmonizer tool generates accessible OKLCH palettes using the APCA contrast algorithm, allowing designers to create color systems with mathematically guaranteed accessibility properties[24][60].

The design token ecosystem achieved a significant milestone in October 2025 when the Design Tokens Community Group released the first stable version of the Design Tokens Specification (version 2025.10)[56]. This standardization directly impacts tool implementations: Figma announced native token import/export support aligned with the DTCG specification[44], Tokens Studio confirmed compliance and added extended features[20], and multiple other tools including Penpot, Sketch, Framer, and Knapsack committed to supporting the standard[56]. This convergence on a shared specification dramatically reduces friction in token file exchange and enables design systems to migrate between tools with minimal rework.

## Practical Implementation Patterns and Complete Examples

Translating architectural principles into working design systems requires concrete, production-tested patterns that address the full complexity of real-world requirements. This section presents comprehensive examples demonstrating how OKLCH tokens integrate with modern design system practices.

### Complete Token File Structure

A production design system typically organizes OKLCH tokens across multiple files that are combined during the build process. Here is a representative structure for a modern design system:

```yaml
# tokens/colors/primitives.yaml
color:
  neutral:
    50:
      $type: color
      $value: oklch(99% 0.001 0)
    100:
      $type: color
      $value: oklch(97% 0.002 0)
    200:
      $type: color
      $value: oklch(90% 0.004 0)
    300:
      $type: color
      $value: oklch(83% 0.006 0)
    400:
      $type: color
      $value: oklch(73% 0.008 0)
    500:
      $type: color
      $value: oklch(60% 0.009 0)
    600:
      $type: color
      $value: oklch(48% 0.008 0)
    700:
      $type: color
      $value: oklch(36% 0.006 0)
    800:
      $type: color
      $value: oklch(24% 0.004 0)
    900:
      $type: color
      $value: oklch(12% 0.002 0)

  blue:
    50:
      $type: color
      $value: oklch(98% 0.008 250)
    100:
      $type: color
      $value: oklch(93% 0.028 250)
    200:
      $type: color
      $value: oklch(80% 0.045 250)
    300:
      $type: color
      $value: oklch(66% 0.056 250)
    400:
      $type: color
      $value: oklch(58% 0.059 250)
    500:
      $type: color
      $value: oklch(49% 0.053 250)
    600:
      $type: color
      $value: oklch(35% 0.042 250)
    700:
      $type: color
      $value: oklch(20% 0.025 250)

  success:
    50:
      $type: color
      $value: oklch(98% 0.009 150)
    100:
      $type: color
      $value: oklch(93% 0.032 150)
    500:
      $type: color
      $value: oklch(49% 0.065 150)
    700:
      $type: color
      $value: oklch(20% 0.034 150)
```

This primitive layer establishes the foundational color palette that all semantic tokens reference. Note that neutral colors maintain zero hue values (or achromatic hue), while colored families maintain consistent hues across all lightness values.

```yaml
# tokens/colors/semantic.yaml
color:
  background:
    primary:
      $type: color
      $value: "{color.neutral.50}"
      $description: Primary background for light mode
    secondary:
      $type: color
      $value: "{color.neutral.100}"
      $description: Secondary background for cards
    tertiary:
      $type: color
      $value: "{color.neutral.200}"
      $description: Tertiary background for subtle layers
    interactive:
      $type: color
      $value: "{color.neutral.75}"
      $description: Background for interactive states

  text:
    primary:
      $type: color
      $value: "{color.neutral.900}"
      $description: Primary text color, maximum contrast
    secondary:
      $type: color
      $value: "{color.neutral.700}"
      $description: Secondary text for supporting information
    tertiary:
      $type: color
      $value: "{color.neutral.500}"
      $description: Tertiary text for minimal emphasis
    inverse:
      $type: color
      $value: "{color.neutral.50}"
      $description: Text color for dark backgrounds

  border:
    default:
      $type: color
      $value: "{color.neutral.200}"
      $description: Default border color
    emphasis:
      $type: color
      $value: "{color.blue.500}"
      $description: Emphasized border for interactive elements

  action:
    primary:
      $type: color
      $value: "{color.blue.500}"
      $description: Primary action color
    success:
      $type: color
      $value: "{color.success.500}"
      $description: Success state indication
    warning:
      $type: color
      $value: oklch(58% 0.15 50)
      $description: Warning state indication
    error:
      $type: color
      $value: oklch(50% 0.20 30)
      $description: Error state indication
```

This semantic layer provides meaningful names that designers and developers use in practice. Tokens reference the primitive palette, enabling global color changes by modifying a single primitive token.

```yaml
# tokens/colors/dark-mode.yaml
color:
  background:
    primary:
      $type: color
      $value: "{color.neutral.900}"
      $description: Primary background for dark mode
    secondary:
      $type: color
      $value: "{color.neutral.800}"
      $description: Secondary background for cards in dark mode
    tertiary:
      $type: color
      $value: "{color.neutral.700}"
      $description: Tertiary background for subtle layers in dark mode
    interactive:
      $type: color
      $value: "{color.neutral.800}"
      $description: Background for interactive states in dark mode

  text:
    primary:
      $type: color
      $value: "{color.neutral.50}"
      $description: Primary text color for dark mode
    secondary:
      $type: color
      $value: "{color.neutral.300}"
      $description: Secondary text for dark mode
    tertiary:
      $type: color
      $value: "{color.neutral.500}"
      $description: Tertiary text for dark mode
    inverse:
      $type: color
      $value: "{color.neutral.900}"
      $description: Text color for light backgrounds in dark mode
```

Dark mode variants reuse the same semantic token names but reference different primitive colors. When these token sets are combined in build processes, CSS generation tools create media query variants that automatically select appropriate colors based on `prefers-color-scheme`.

### Component-Level Token Integration

At the component level, design systems should define tokens for specific UI patterns while remaining abstract enough to reuse across variants. Here is an example for button styling:

```yaml
# tokens/components/button.yaml
component:
  button:
    primary:
      background:
        $type: color
        $value: "{color.action.primary}"
      background-hover:
        $type: color
        $value: oklch(from {color.action.primary} calc(l - 0.15) c h)
      background-active:
        $type: color
        $value: oklch(from {color.action.primary} calc(l - 0.25) c h)
      text:
        $type: color
        $value: "{color.text.inverse}"
      border:
        $type: color
        $value: "{color.action.primary}"

    secondary:
      background:
        $type: color
        $value: "{color.background.secondary}"
      background-hover:
        $type: color
        $value: "{color.background.tertiary}"
      background-active:
        $type: color
        $value: "{color.neutral.200}"
      text:
        $type: color
        $value: "{color.text.primary}"
      border:
        $type: color
        $value: "{color.border.default}"

    disabled:
      background:
        $type: color
        $value: "{color.background.secondary}"
      text:
        $type: color
        $value: "{color.text.tertiary}"
      border:
        $type: color
        $value: "{color.border.default}"
```

Notice that component tokens directly reference semantic colors but also demonstrate the power of OKLCH's relative color syntax. The `background-hover` and `background-active` values adjust the lightness of the primary button color using `oklch(from ...)` syntax, maintaining hue and chroma while reducing brightness. This pattern automatically works across all color variants—primary, secondary, and disabled buttons all achieve consistent visual hierarchy through lightness adjustment.

### Build Process Configuration

A complete Style Dictionary configuration might appear as:

```javascript
// style-dictionary.config.js
const StyleDictionary = require('style-dictionary');

StyleDictionary.registerFilter({
  name: 'isColor',
  matcher: (token) => token.$type === 'color'
});

module.exports = {
  source: [
    'tokens/colors/primitives.yaml',
    'tokens/colors/semantic.yaml',
    'tokens/colors/dark-mode.yaml',
    'tokens/components/**/*.yaml'
  ],
  
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',
        filter: 'isColor'
      }]
    },

    json: {
      transformGroup: 'js',
      buildPath: 'dist/json/',
      files: [{
        destination: 'tokens.json',
        format: 'json/flat',
        filter: 'isColor'
      }]
    },

    ios: {
      transformGroup: 'ios-swift',
      buildPath: 'dist/ios/',
      files: [{
        destination: 'Colors.swift',
        format: 'ios/colors.swift',
        filter: 'isColor'
      }]
    }
  }
};
```

During the build process, Style Dictionary parses the YAML token definitions, applies platform-specific transformations, and generates output. For CSS, this produces:

```css
:root {
  --color-neutral-50: rgb(255, 255, 254);
  --color-neutral-50-p3: color(display-p3 0.998 0.998 0.996);
  --color-neutral-50-oklch: oklch(99% 0.001 0);
  
  --color-blue-500: rgb(0, 119, 204);
  --color-blue-500-p3: color(display-p3 0.15 0.50 0.85);
  --color-blue-500-oklch: oklch(49% 0.053 250);
  
  --color-background-primary: var(--color-neutral-50);
  --color-text-primary: var(--color-neutral-900);
  
  --component-button-primary-background: var(--color-action-primary);
  --component-button-primary-background-hover: oklch(from var(--color-action-primary) calc(l - 0.15) c h);
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background-primary: var(--color-neutral-900);
    --color-text-primary: var(--color-neutral-50);
  }
}
```

This output provides multiple fallback options for maximum compatibility while maintaining the original OKLCH specifications for browsers that support them.

## Conclusion and Recommendations for Design System Evolution

The integration of OKLCH color space into design token systems represents a paradigm shift that extends far beyond a mere technical substitution of one color model for another. By leveraging perceptually uniform color mathematics, OKLCH enables design systems to scale with confidence, maintain accessibility automatically, and achieve consistency across multiple themes and platforms with minimal manual effort. The maturation of tooling, standardization through the DTCG specification, and broad adoption across leading design platforms have created a genuine inflection point where OKLCH has transitioned from experimental research to production standard practice.

The architectural principles outlined in this report—organizing tokens through multiple hierarchical levels, mapping OKLCH components to semantic meaning, implementing systematic gamut mapping, and establishing clear accessibility guidelines—provide design system teams with a robust foundation for modernizing their color management infrastructure. Organizations implementing OKLCH-based design systems in 2025-2026 should prioritize establishing clear documentation of their specific color space choices, developing appropriate testing and validation processes to verify behavior across target devices and platforms, and investing in tooling and build process improvements that automate the complex transformations required to support multiple platforms simultaneously[2][9][25][56].

For design systems currently operating with RGB or HSL color specifications, the migration to OKLCH can be undertaken gradually. Implementing OKLCH alongside existing color specifications allows teams to adopt the new system incrementally while maintaining backward compatibility[38]. Beginning with new token definitions in OKLCH format while maintaining existing RGB specifications enables teams to experience the benefits of perceptual uniformity for new components while avoiding the risk of breaking changes to established systems[4][38].

The future evolution of design token systems will likely see continued refinement of accessibility algorithms, particularly as WCAG 3 and APCA specifications achieve broader adoption[34][57]. Design system teams should remain engaged with emerging standards and tooling, as improvements in contrast algorithms and perceptual color science will enable even more sophisticated automation of accessibility assurance within design systems[34][57]. Additionally, as native OKLCH support within mainstream design tools like Figma and Sketch continues to improve, friction in design-to-code workflows will decrease further, enabling design systems to operate with greater efficiency and reduced manual color format conversions[4][19].

The architectural patterns and implementation approaches detailed in this report represent current best practices established through production use in leading design systems and validated through the collaborative work of the Design Tokens Community Group[56]. By following these principles while remaining responsive to emerging tools and standards, design system teams can establish color management infrastructure that will serve their organizations effectively through the evolution of design technology and the continuing expansion of design system capabilities.

---

## Citations

1. https://www.designtokens.org/tr/drafts/color/
2. https://mohanvadivel.com/thoughts/building-accessible-color-system
3. https://cobalt-ui.pages.dev/guides/tokens
4. https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611
5. https://www.figma.com/community/plugin/1560632211514322267/prism-oklch-colour-palette-generator
6. https://firefox-source-docs.mozilla.org/toolkit/themes/shared/design-system/docs/README.json-design-tokens.stories.html
7. https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611
8. https://www.figma.com/community/plugin/1520709447715571667/supa-design-tokens
9. https://www.ethangardner.com/posts/supporting-color-contrast-accessibility/
10. https://www.designtokens.org/TR/2025.10/color/
11. https://www.figma.com/community/plugin/1534554794837682758/push-ui-design-tokens
12. https://firefox-source-docs.mozilla.org/toolkit/themes/shared/design-system/docs/README.json-design-tokens.stories.html
13. https://blog.heronhq.com/en/best-practices-for-building-a-color-system-in-figma/
14. https://color-contrast.incluud.dev/design-tokens/
15. https://github.com/design-tokens/community-group/issues/137
16. https://m3.material.io/styles/color/roles
17. https://www.ethangardner.com/posts/supporting-color-contrast-accessibility/
18. https://www.designtokens.org/tr/drafts/color/
19. https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611
20. https://docs.tokens.studio/manage-tokens/token-sets
21. https://uploadcare.com/blog/oklch-in-css/
22. https://evilmartians.com/chronicles/better-dynamic-themes-in-tailwind-with-oklch-color-magic
23. https://www.figma.com/community/plugin/843461159747178978/tokens-studio-for-figma
24. https://evilmartians.com/chronicles/exploring-the-oklch-ecosystem-and-its-tools
25. https://www.contentful.com/blog/design-token-system/
26. https://mohanvadivel.com/thoughts/building-accessible-color-system
27. https://www.styleframe.dev/docs/design-tokens
28. https://www.designtokens.org/tr/drafts/color/
29. https://m3.material.io/styles/color/system/how-the-system-works
30. https://keithjgrant.com/posts/2024/06/a-structured-approach-to-custom-properties/
31. https://www.w3.org/TR/css-color-5/
32. https://www.designtokens.org/tr/drafts/color/
33. https://oklch.com
34. https://arxiv.org/html/2512.05067v1
35. https://javascript.plainenglish.io/the-tiny-css-upgrade-that-solves-big-design-system-headaches-3d933675bf76
36. https://oklch-palette.vercel.app
37. https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611
38. https://www.npmjs.com/package/@csstools/postcss-oklab-function
39. https://www.designtokens.org/TR/2025.10/format/
40. https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl
41. https://css-tricks.com/almanac/functions/o/oklch/
42. https://penpot.app/blog/design-tokens-for-designers/
43. https://facelessuser.github.io/coloraide/gamut/
44. https://zeroheight.com/blog/building-scalable-design-systems-with-figma-26-tips-for-2026/
45. https://blog.logrocket.com/oklch-css-consistent-accessible-color-palettes/
46. https://oklch.com
47. https://uxdesign.cc/design-tokens-with-confidence-862119eb819b
48. https://www.designsystemscollective.com/dark-mode-done-right-building-adaptive-design-systems-5f220f656b9f
49. https://blog.heronhq.com/en/best-practices-for-building-a-color-system-in-figma/
50. https://uxdesign.cc/naming-design-tokens-9454818ed7cb
51. https://utilitybend.com/blog/oklchroma-an-oklch-color-pattern-generator-that-generates-css-variables
52. https://m3.material.io/styles/color/roles
53. https://www.designsystemscollective.com/color-as-strategy-building-systems-with-intent-a89c0934983d
54. https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties
55. https://terrazzo.app/docs/reference/tokens/
56. https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
57. https://www.figma.com/community/plugin/1383061356258316633/text-contrast-checker-apca-wcag3
58. https://www.gfor.rest/blog/advanced-design-utils-colors
59. https://www.zeroheight.com/blog/whats-new-in-the-design-tokens-spec/
60. https://evilmartians.com/chronicles/exploring-the-oklch-ecosystem-and-its-tools

---

## Usage Stats

- Prompt tokens: 159
- Completion tokens: 9874
- Total tokens: 10033
