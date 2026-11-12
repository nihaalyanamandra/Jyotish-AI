export type Birth={date:string;time:string;timezone:string;latitude:number;longitude:number};
export type Placement={longitude:number;sign:string;degree:number;house:number;nakshatra:{name:string;pada:number;lord:string};retrograde?:boolean};
export type Dasha={lord:string;start:string;end:string;subperiods:{lord:string;start:string;end:string}[]};
export type Chart={ascendant:Placement;planets:Record<string,Placement>;divisional:Record<string,{ascendant:string;planets:Record<string,{sign:string;house:number}>}>;dashas:Dasha[];ayanamsa:string;house_system:string;ephemeris:string};
