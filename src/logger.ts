export function canonicalize(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    if (Array.isArray(obj)) {
        return obj.map(canonicalize);
    }
    const keys = Object.keys(obj);
    if (keys.length <= 1) {
        if (keys.length === 1) {
            return { [keys[0]]: canonicalize(obj[keys[0]]) };
        }
        return {};
    }
    keys.sort();
    const result: any = {};
    for (const key of keys) {
        result[key] = canonicalize(obj[key]);
    }
    return result;
}
