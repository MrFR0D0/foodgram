import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <b>Python:</b> основной язык для бэкенда.
              </li>
              <li className={styles.textItem}>
                <b>Django:</b> веб-фреймворк для разработки серверной части.
              </li>
              <li className={styles.textItem}>
                <b>Django REST Framework:</b> для создания гибкого и мощного API.
              </li>
              <li className={styles.textItem}>
                <b>PostgreSQL:</b> в качестве основной реляционной базы данных.
              </li>
              <li className={styles.textItem}>
                <b>React:</b> для построения динамического и отзывчивого пользовательского интерфейса.
              </li>
              <li className={styles.textItem}>
                <b>Docker и Docker Compose:</b> для контейнеризации и оркестрации всего приложения.
              </li>
              <li className={styles.textItem}>
                <b>Nginx:</b> в качестве веб-сервера и обратного прокси для раздачи статики и перенаправления запросов.
              </li>
              <li className={styles.textItem}>
                <b>Gunicorn:</b> как WSGI-сервер для запуска Django-приложения в продакшене.
              </li>
              <li className={styles.textItem}>
                <b>GitHub Actions:</b> для автоматизации процессов CI/CD (непрерывной интеграции и доставки).
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

