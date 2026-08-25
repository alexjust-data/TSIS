import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import './atlas.css';

const sans=Geist({variable:'--font-geist-sans',subsets:['latin']});
const mono=Geist_Mono({variable:'--font-geist-mono',subsets:['latin']});
export const metadata:Metadata={title:'TSIS Daily Pattern Atlas',description:'Explorador local de activaciones, trayectorias y episodios daily.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="es"><body className={`${sans.variable} ${mono.variable}`}>{children}</body></html>}