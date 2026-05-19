export const APPEARANCE_SYSTEM = 'system';
export const APPEARANCE_LIGHT = 'light';
export const APPEARANCE_DARK = 'dark';

export const APPEARANCE_MODES = [
    APPEARANCE_SYSTEM,
    APPEARANCE_LIGHT,
    APPEARANCE_DARK,
];

export function normalizeAppearanceMode(mode){
    if(APPEARANCE_MODES.indexOf(mode) >= 0){
        return mode;
    }
    return APPEARANCE_SYSTEM;
}

export function resolveAppearance(mode, prefersDark){
    const normalized = normalizeAppearanceMode(mode);
    if(normalized === APPEARANCE_DARK){
        return APPEARANCE_DARK;
    }
    if(normalized === APPEARANCE_LIGHT){
        return APPEARANCE_LIGHT;
    }
    return prefersDark ? APPEARANCE_DARK : APPEARANCE_LIGHT;
}

export function getNextAppearanceMode(mode){
    const normalized = normalizeAppearanceMode(mode);
    if(normalized === APPEARANCE_SYSTEM){
        return APPEARANCE_LIGHT;
    }
    if(normalized === APPEARANCE_LIGHT){
        return APPEARANCE_DARK;
    }
    return APPEARANCE_SYSTEM;
}

export function getAppearanceLabel(mode, resolved){
    const normalized = normalizeAppearanceMode(mode);
    if(normalized === APPEARANCE_SYSTEM){
        return resolved === APPEARANCE_DARK ? '跟随系统 · 夜' : '跟随系统 · 昼';
    }
    if(normalized === APPEARANCE_DARK){
        return '暗夜';
    }
    return '昼间';
}

export function applyAppearanceToDocument(mode, resolved){
    if(typeof document === 'undefined'){
        return;
    }
    const normalized = normalizeAppearanceMode(mode);
    const actual = resolved === APPEARANCE_DARK ? APPEARANCE_DARK : APPEARANCE_LIGHT;
    const root = document.documentElement;
    root.setAttribute('data-horosa-appearance-mode', normalized);
    root.setAttribute('data-horosa-appearance', actual);
    document.body.setAttribute('data-horosa-appearance', actual);
}
