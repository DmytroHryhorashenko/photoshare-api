import { useEffect } from 'react'
import HeroSection from '../components/landing/HeroSection'
import StatsSection from '../components/landing/StatsSection'
import FeaturesSection from '../components/landing/FeaturesSection'
import ArchitectureSection from '../components/landing/ArchitectureSection'
import TechStackSection from '../components/landing/TechStackSection'
import ApiPreviewSection from '../components/landing/ApiPreviewSection'
import MetricsSection from '../components/landing/MetricsSection'
import ScreenshotsSection from '../components/landing/ScreenshotsSection'
import FooterSection from '../components/landing/FooterSection'

export default function Landing() {
  useEffect(() => {
    const hash = window.location.hash.replace('#', '')
    if (hash) {
      requestAnimationFrame(() => {
        document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth' })
      })
    }
  }, [])

  return (
    <>
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <ArchitectureSection />
      <TechStackSection />
      <ApiPreviewSection />
      <MetricsSection />
      <ScreenshotsSection />
      <FooterSection />
    </>
  )
}
