"use strict";(self.webpackChunk_xpay_wallet_hub=self.webpackChunk_xpay_wallet_hub||[]).push([[470],{79033:(e,t,n)=>{var a=n(7364),s=n(91689),r=n(37814);window.loadXpayHubI18n=function(){const e=e=>import(`./json/i18n-hub/${e}/strings.json`,{with:{type:"json"}}),t=e=>import(`./json/i18n-shared-components/${e}/strings.json`,{with:{type:"json"}}),n=e=>t(e).catch((()=>t((0,a.Hg)(e)))).catch((()=>{Promise.resolve({})})),o=e=>t(e).catch((()=>(e=>import(`./json/i18n-e-tree-shared/${e}/strings.json`,{with:{type:"json"}}))((0,a.Hg)(e)))).catch((()=>{Promise.resolve({})}));return async(t=null)=>{const i=(0,a.JK)();return(0,a.mJ)(i)?Promise.resolve():Promise.all([(l=i,e(l).catch((()=>e((0,a.Hg)(l)))).catch((()=>{Promise.resolve({})}))),n(i),o(i)]).then((e=>{const n=e[0],a=e[1],o=e[2];let i;if(!i){const{loadTimeData:e}=window;i=e}n&&n.default&&i.overrideValues((0,s.A)(t)?(0,r.A)(n.default,((e,n)=>-1!==t.indexOf(n))):n.default),a&&a.default&&i.overrideValues((0,s.A)(t)?(0,r.A)(a.default,((e,n)=>-1!==t.indexOf(n))):a.default),o&&o.default&&i.overrideValues((0,s.A)(t)?(0,r.A)(o.default,((e,n)=>-1!==t.indexOf(n))):o.default)}));var l}}()},7364:(e,t,n)=>{n.d(t,{Hg:()=>a,JK:()=>r,mJ:()=>s});const a=e=>{const t=e??"";switch(t){case"en-au":case"en-AU":return"en-GB";case"zh-TW":return"zh-Hant";case"zh-CN":return"zh-Hans"}const n=t.split("-")?.[0];switch(n){case"pt":return"pt-PT";case"zh":return"zh-Hans";default:return`${n}`}},s=e=>"en-US"===e||"en-us"===e||"en"===e,r=()=>window.loadTimeData?.data_?.locale||navigator.language}},e=>{e.O(0,[502],(()=>e(e.s=79033))),e.O()}]);