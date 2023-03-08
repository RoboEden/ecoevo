export const funcInitialState = () => {
    return {
        sliderStep: 0,
        cacheStep: 0,
        renderStep: 0,
        currTime: performance.now(),
        needLoad: true,
        isLoading: true,
        isPlaying: false,
        actions: null,
        log: '',
        data: {},
        mapSize: undefined,
        totalStep: undefined,
        clickedId: undefined,
        bagVolume: undefined,
    }
}

export function appReducer(state, action) {
    if (!state) {
        return funcInitialState()
    }
    switch (action.type) {
        /**
         *  Load related
         */

        case 'LOG': {
            return {
                ...state,
                log: action.log
            }
        }
        case 'INIT': {
            return {
                ...state,
                mapSize: action.mapSize,
                totalStep: action.totalStep,
                bagVolume: action.bagVolume,
            }
        }
        case 'LOADED': {
            return {
                ...state,
                isLoading: false
            }
        }
        case 'LOADING': {
            return {
                ...state,
                isLoading: true
            }
        }
        /**
         *  Step related
         */
        case 'SLIDER_STEP': {
            return {
                ...state,
                sliderStep: action.sliderStep,
            }
        }
        case 'RENDER_STEP': {
            return {
                ...state,
                renderStep: action.renderStep,
                currTime: performance.now()
            }
        }
        case 'CACHE_STEP': {
            return {
                ...state,
                cacheStep: action.cacheStep,
            }
        }
        /**
        *  Play related
        */
        case 'PAUSE': {
            return {
                ...state,
                isPlaying: false,
            }
        }
        case 'PLAY': {
            const newValue = Math.min(state.renderStep + 1, state.cacheStep)
            return {
                ...state,
                isPlaying: true,
                sliderStep: newValue,
                renderStep: newValue,
                // currTime: performance.now()
            }
        }
        /**
        *  Data related
        */
        case 'DATA': {
            return {
                ...state,
                data: action.data
            }
        }
        case 'CLICKED_ID': {
            return {
                ...state,
                clickedId: action.clickedId
            }
        }
        /**
        *  Unused
        */
        case 'RESET': {
            return {
                ...state,
            }
        }
        case 'CTRL_ACTION': {
            return {
                ...state,
                actions: action.actions,
                step: action.step
            }
        }
    }
    throw Error('Unknown action: ' + action.type);
}