package org.futo.inputmethod.latin.uix.theme.presets

import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import org.futo.inputmethod.latin.R
import org.futo.inputmethod.latin.uix.extendedDarkColorScheme
import org.futo.inputmethod.latin.uix.theme.ThemeOption
import org.futo.inputmethod.latin.uix.theme.selector.ThemePreview

/**
 * A warm dark grey theme with a terracotta enter key, matching the Gboard layout this
 * fork's dimensions were derived from.
 *
 * The values come from measuring a screenshot of that keyboard pixel by pixel rather
 * than from eyeballing it. The panel is a vertical gradient that darkens toward the
 * bottom, and the keycaps are translucent white over it rather than a flat fill, which
 * is why they get darker down the keyboard:
 *
 *  - panel gradient   #5C5754 at the top to #1B1112 at the bottom
 *  - regular keycaps  white at ~0.19 alpha (fitted across rows against the background)
 *  - functional keys  white at ~0.07 alpha (shift, ?123, backspace)
 *  - enter key        solid #B45736
 *  - glyphs           #FFFFFF
 */
private val compactSlateScheme = extendedDarkColorScheme(
    primary = Color(0xFFB45736),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFF7A3520),
    onPrimaryContainer = Color(0xFFFFDBCF),
    secondary = Color(0xFFE0BEB2),
    onSecondary = Color(0xFF442A21),
    secondaryContainer = Color(0xFF5D4036),
    onSecondaryContainer = Color(0xFFFFDBCF),
    tertiary = Color(0xFFD8C58E),
    onTertiary = Color(0xFF3A2F05),
    tertiaryContainer = Color(0xFF52461A),
    onTertiaryContainer = Color(0xFFF5E1A8),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005),
    errorContainer = Color(0xFF93000A),
    onErrorContainer = Color(0xFFFFDAD6),
    outline = Color(0xFFA08C85),
    outlineVariant = Color(0xFF52453F),
    surface = Color(0xFF1B1112),
    onSurface = Color(0xFFF0E0DC),
    onSurfaceVariant = Color(0xFFD8C2BC),
    surfaceContainerHighest = Color(0xFF4A403E),
    shadow = Color(0xFF000000).copy(alpha = 0.7f),

    keyboardSurface = Color(0xFF3A3332),
    keyboardSurfaceDim = Color(0xFF2B2422),
    keyboardContainer = Color(0xFFFFFFFF).copy(alpha = 0.19f),
    keyboardContainerVariant = Color(0xFFFFFFFF).copy(alpha = 0.07f),
    onKeyboardContainer = Color(0xFFFFFFFF),
    keyboardPress = Color(0xFFFFFFFF).copy(alpha = 0.32f),
    primaryTransparent = Color(0xFFB45736).copy(alpha = 0.3f),
    onSurfaceTransparent = Color(0xFFF0E0DC).copy(alpha = 0.1f),

    keyboardBackgroundGradient = Brush.verticalGradient(
        0.0f to Color(0xFF5C5754),
        1.0f to Color(0xFF1B1112)
    ),
    navigationBarColor = Color(0xFF1B1112),
    navigationBarColorForTransparency = Color(0xFF000000),
)

val CompactSlate = ThemeOption(
    dynamic = false,
    key = "CompactSlate",
    name = R.string.theme_compact_slate,
    available = { true }
) {
    compactSlateScheme
}

@Composable
@Preview
private fun PreviewThemeCompactSlate() {
    ThemePreview(CompactSlate)
}
