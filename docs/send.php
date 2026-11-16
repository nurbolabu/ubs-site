<?php
/**
 * UBS — form handler for hoster.kz (PHP mail()).
 * Receives the consultation forms and e-mails them to MAIL_TO.
 * Answers JSON: {"ok":true} / {"ok":false,"error":"..."}
 */
declare(strict_types=1);

const MAIL_TO   = 'ubs@ubsystem.kz';           // recipient(s), comma separated
const MAIL_FROM = 'ubs@ubsystem.kz';           // must be a real mailbox of ubsystem.kz on the same hosting
const SITE_NAME = 'UBS website';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

function reply(bool $ok, string $error = ''): void {
    http_response_code($ok ? 200 : 400);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    reply(false, 'method');
}
// honeypot: bots fill the hidden "website" field
if (!empty($_POST['website'])) {
    reply(true);
}
// simple rate limit: one message per 20 seconds per visitor
session_start();
if (isset($_SESSION['ubs_last']) && time() - $_SESSION['ubs_last'] < 20) {
    reply(false, 'too_fast');
}

function field(string $name, int $max = 200): string {
    $v = isset($_POST[$name]) ? trim((string)$_POST[$name]) : '';
    $v = str_replace(["\r", "\n"], ' ', $v);
    return mb_substr(strip_tags($v), 0, $max);
}

$name    = field('name', 120);
$email   = field('email', 160);
$phone   = field('phone', 40);
$company = field('company', 160);
$page    = field('page', 300);
$lang    = field('lang', 5);

if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reply(false, 'email');
}
if ($name === '' && $company === '') {
    reply(false, 'name');
}

$rows = [
    'Name'    => $name,
    'Company' => $company,
    'E-mail'  => $email,
    'Phone'   => $phone,
    'Page'    => $page,
    'Language'=> $lang,
    'Date'    => date('Y-m-d H:i'),
    'IP'      => $_SERVER['REMOTE_ADDR'] ?? '',
];
$body = '';
foreach ($rows as $k => $v) {
    if ($v !== '') {
        $body .= $k . ': ' . $v . "\n";
    }
}

$subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта UBS / Request from website') . '?=';
$headers = implode("\r\n", [
    'From: ' . '=?UTF-8?B?' . base64_encode(SITE_NAME) . '?= <' . MAIL_FROM . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

$sent = @mail(MAIL_TO, $subject, $body, $headers, '-f' . MAIL_FROM);
if (!$sent) {
    reply(false, 'mail');
}
$_SESSION['ubs_last'] = time();
reply(true);
