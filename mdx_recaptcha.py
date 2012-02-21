from recaptcha.client.mailhide import _doterizeemail, asurl
import markdown


class ReCaptchaExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        r = ReCaptchaMailPattern(markdown.inlinepatterns.AUTOMAIL_RE, md)
        if not self.getConfig('recaptcha_public_key') or not self.getConfig('recaptcha_private_key'):
            raise ValueError('missing recaptcha key')

        r.public_key = self.getConfig('recaptcha_public_key')
        r.private_key = self.getConfig('recaptcha_private_key')
        md.inlinePatterns['automail'] = r


def makeExtension(configs={}):
    return ReCaptchaExtension(configs=dict(configs))


class ReCaptchaMailPattern(markdown.inlinepatterns.Pattern):
    """
    Return a ReCaptchaMail link Element given an automail link (`<foo@example.com>`).
    """
    def handleMatch(self, m):
        el = markdown.util.etree.Element('span')

        link = markdown.util.etree.Element('a')
        email = self.unescape(m.group(2))
        if email.startswith("mailto:"):
            email = email[len("mailto:"):]

        url = asurl(email, self.public_key, self.private_key)

        (userpart, domainpart) = _doterizeemail(email)
        prefix = markdown.util.etree.Element('span')
        prefix.text = markdown.util.AtomicString(userpart)
        link.text = markdown.util.AtomicString('...')
        link.set('href', url)
        postfix = markdown.util.etree.Element('span')
        postfix.text = markdown.util.AtomicString(domainpart)

        el.extend([prefix, link, postfix])

        return el
