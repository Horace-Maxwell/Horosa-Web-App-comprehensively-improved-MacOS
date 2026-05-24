import { handleError } from './utils/helper';
import { installWindowSizePersistence } from './utils/windowSizePersistence';

if (typeof window !== 'undefined' && typeof EventTarget !== 'undefined') {
    const proto = EventTarget.prototype;
    const addEventListener = proto && proto.addEventListener;
    if (addEventListener && !window.__horosaDomNodeInsertedPatched) {
        proto.addEventListener = function(type, listener, options) {
            if (type === 'DOMNodeInserted') {
                return;
            }
            return addEventListener.call(this, type, listener, options);
        };
        window.__horosaDomNodeInsertedPatched = true;
    }
}

installWindowSizePersistence();

export const dva = {
    config: {
        onError(err) {
            console.log(err);
            handleError(err);
        },
    },
}
