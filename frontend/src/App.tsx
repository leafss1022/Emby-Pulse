import { Layout } from '@/components/Layout'
import { NowPlaying } from '@/components/NowPlaying'
import { Overview, Content, Users, Devices, History, Login } from '@/pages'
import { AnimatePresence, motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useFilter } from '@/contexts/FilterContext'
import { Loader2 } from 'lucide-react'

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
}

const pageTransition = {
  type: 'spring' as const,
  stiffness: 380,
  damping: 30,
  mass: 0.8,
}

function App() {
  const { isAuthenticated, isLoading } = useAuth()
  const { buildQueryParams } = useFilter()

  // 加载中显示
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    )
  }

  // 未登录显示登录页
  if (!isAuthenticated) {
    return <Login />
  }

  const filterParams = buildQueryParams()

  return (
    <Layout>
      {({ activeTab, refreshKey }) => (
        <>
          {/* Now Playing - shown on all tabs */}
          <NowPlaying />

          {/* Tab Content with Animation */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${activeTab}-${refreshKey}`}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={pageTransition}
            >
              {activeTab === 'overview' && <Overview filterParams={filterParams} />}
              {activeTab === 'content' && <Content filterParams={filterParams} />}
              {activeTab === 'users' && <Users filterParams={filterParams} />}
              {activeTab === 'devices' && <Devices filterParams={filterParams} />}
              {activeTab === 'history' && <History filterParams={filterParams} />}
            </motion.div>
          </AnimatePresence>
        </>
      )}
    </Layout>
  )
}

export default App
